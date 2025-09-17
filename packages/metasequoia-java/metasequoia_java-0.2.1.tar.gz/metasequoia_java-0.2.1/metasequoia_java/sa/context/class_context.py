"""
类上下文
"""

import functools
from typing import List, Optional, Tuple

from metasequoia_java import ast
from metasequoia_java.common import LOGGER
from metasequoia_java.sa.context.base_context import ClassContext
from metasequoia_java.sa.context.base_context import FileContext
from metasequoia_java.sa.context.base_context import ProjectContext
from metasequoia_java.sa.elements import RuntimeClass
from metasequoia_java.sa.name_space import NameSpace
from metasequoia_java.sa.name_space import SimpleNameSpace

__all__ = [
    "ClassContextImp"
]


class ClassContextImp(ClassContext):
    """类上下文管理类的实现类"""

    def __init__(self,
                 project_context: ProjectContext,
                 file_context: FileContext,
                 class_name: str,
                 class_node: ast.Class,
                 outer_class_context: Optional["ClassContext"] = None):
        self._project_context = project_context
        self._file_context = file_context
        self._class_name = class_name  # 如果当前类为匿名类，则为 Anonymous  # TODO 考虑是否有更优方法
        self._class_node = class_node

        # 如果当前类为内部类，则指向外部类的上下文管理器，否则为 None
        self._outer_class_context = outer_class_context

        self._simple_name_space = SimpleNameSpace.create_by_class(class_node)

    @staticmethod
    def create_by_class_name(file_context: FileContext, class_name: str) -> Optional["ClassContextImp"]:
        """根据类型构造 ClassContext 对象"""
        if file_context is None:
            return None

        if "." in class_name:
            class_node = file_context.file_node.get_inner_class_by_name(class_name)  # 根据内部类名获取类的抽象语法树节点
            outer_class_name = class_name[:class_name.rindex(".")]
            outer_class_context = ClassContextImp.create_by_class_name(file_context, outer_class_name)
        else:
            class_node = file_context.file_node.get_class_by_name(class_name)  # 根据类名获取类的抽象语法树节点
            outer_class_context = None

        if class_node is None:
            return None

        return ClassContextImp(
            project_context=file_context.project_context,
            file_context=file_context,
            class_name=class_name,
            class_node=class_node,
            outer_class_context=outer_class_context
        )

    @property
    def project_context(self) -> ProjectContext:
        """返回所属项目上下文管理器"""
        return self._project_context

    @property
    def file_context(self) -> FileContext:
        """返回所属文件上下文管理器"""
        return self._file_context

    @property
    def class_name(self) -> str:
        """返回类名"""
        return self._class_name

    @property
    def class_node(self) -> ast.Class:
        """返回类的抽象语法树节点"""
        return self._class_node

    @property
    def outer_class_context(self) -> Optional["ClassContext"]:
        """返回外部类的 ClassContext 对象（仅当当前类为内部类时不为 None）"""
        return self._outer_class_context

    def get_method_node_by_name(self, method_name: str) -> Optional[Tuple[ClassContext, ast.Method]]:
        """根据 method_name 获取方法所在类的 ClassContext 和抽象语法树节点"""
        # 优先在当前类中寻找方法
        method_node = self.class_node.get_method_by_name(method_name)
        if method_node is not None:
            return self, method_node

        # 在外部类中查找方法
        if self.outer_class_context is not None:
            method_node = self.outer_class_context.class_node.get_method_by_name(method_name)
            if method_node is not None:
                return self.outer_class_context, method_node

        # 尝试在父类中寻找方法（原则上只会有一个父类中包含）
        for runtime_class in self.get_extends_and_implements():
            class_context = self.project_context.create_class_context_by_runtime_class(
                runtime_class=runtime_class,
                need_warning=False
            )
            if class_context is None:
                LOGGER.warning(
                    f"在尝试在 {self.file_context.package_name}.{self.class_name} 中寻找 {method_name} 方法时，尝试在父类中寻找方法，"
                    f"但在项目中找不到父类 {runtime_class.absolute_name}")
                continue

            method_info = class_context.get_method_node_by_name(method_name)
            if method_info is not None:
                return method_info
        return None

    def get_variable_node_by_name(self,
                                  variable_name: str,
                                  need_warning: bool = True) -> Optional[Tuple[ClassContext, ast.Variable]]:
        """根据 variable_name 获取类变量所在类的 ClassContext 和抽象语法树节点"""
        # 优先在当前类中寻找属性
        variable_node = self.class_node.get_variable_by_name(variable_name)
        if variable_node is not None:
            return self, variable_node

        # 在外部类中寻找属性
        if self.outer_class_context is not None:
            variable_node = self.outer_class_context.class_node.get_variable_by_name(variable_name)
            if variable_node is not None:
                return self.outer_class_context, variable_node

        # 尝试在父类中寻找属性
        for runtime_class in self.get_extends_and_implements():
            class_context = self.project_context.create_class_context_by_runtime_class(
                runtime_class=runtime_class,
                need_warning=False
            )
            if class_context is None:
                if need_warning is True:
                    LOGGER.warning(f"尝试在父类中获取属性时，在项目中找不到 runtime_class: {runtime_class}")
                continue

            variable_info = class_context.get_variable_node_by_name(variable_name)
            if variable_info is not None:
                return variable_info

        return None

    @functools.lru_cache(maxsize=10)
    def get_extends_and_implements(self) -> List[RuntimeClass]:
        """获取继承和实现接口的类的 RuntimeClass 对象的列表"""
        result = []
        for type_node in self.class_node.get_extends_and_implements():
            # 获取继承的类名
            class_name = None
            if isinstance(type_node, ast.Identifier):
                class_name = type_node.name
            elif isinstance(type_node, ast.ParameterizedType):
                type_name = type_node.type_name
                if isinstance(type_name, ast.Identifier):
                    class_name = type_name.name

            if class_name is None:
                LOGGER.warning(f"无法处理的类名类型: {type_node}")
                continue

            runtime_class = self.file_context.infer_runtime_class_by_identifier_name(class_name)
            if runtime_class is None:
                LOGGER.warning(f"找不到继承类: class_name={class_name}")
                continue
            package_name = runtime_class.package_name
            if package_name is None:
                LOGGER.warning(f"找不到继承类所属的包: class_name={class_name}")
                continue

            result.append(RuntimeClass.create(
                package_name=package_name,
                public_class_name=class_name,
                class_name=class_name,
                type_arguments=[]
            ))
        return result

    def get_runtime_class(self) -> RuntimeClass:
        """构造当前类上下文对应的 RuntimeClass 对象"""
        return RuntimeClass.create(
            package_name=self.file_context.package_name,
            public_class_name=self.file_context.public_class_name,
            class_name=self.class_name,
            type_arguments=None
        )

    # ------------------------------ 命名空间管理器 ------------------------------

    def get_simple_name_space(self) -> SimpleNameSpace:
        """返回类变量的单层命名空间"""
        return self._simple_name_space

    def get_name_space(self) -> NameSpace:
        """返回包含类变量的命名空间"""
        return NameSpace(self._simple_name_space)

    # ------------------------------ 元素类型推断 ------------------------------

    def infer_runtime_class_by_node(self,
                                    runtime_class: RuntimeClass,
                                    type_node: Optional[ast.Tree],
                                    is_not_variable: bool = False) -> Optional[RuntimeClass]:
        """推断出现在当前类中的抽象语法树类型"""
        if type_node is None:
            return None

        if isinstance(type_node, ast.Identifier):
            return self.infer_runtime_class_by_identifier_name(runtime_class, type_node.name, is_not_variable=True)

        if isinstance(type_node, ast.ParameterizedType):
            class_name = type_node.type_name.generate()
            if "." not in class_name:
                # "类名"
                package_name = None
                if sub_runtime_class := self.infer_runtime_class_by_identifier_name(runtime_class, class_name):
                    package_name = sub_runtime_class.package_name
            else:  # TODO 待优化处理逻辑
                # "包名.类名"
                package_name = class_name[:class_name.rindex(".")]
                class_name = class_name[class_name.rindex(".") + 1:]
                if self.file_context.import_contains_class_name(package_name):
                    # "主类名.子类名"
                    main_class_name = package_name  # 主类名
                    package_name = None
                    if sub_runtime_class := self.infer_runtime_class_by_identifier_name(runtime_class, main_class_name):
                        package_name = sub_runtime_class.package_name
                    class_name = f"{main_class_name}.{class_name}"
            type_arguments = [
                self.infer_runtime_class_by_node(runtime_class, argument, is_not_variable=is_not_variable)
                for argument in type_node.type_arguments
            ]
            return RuntimeClass.create(
                package_name=package_name,
                public_class_name=class_name,
                class_name=class_name,
                type_arguments=type_arguments
            )

        return self.file_context.infer_runtime_class_by_node(type_node)

    def infer_runtime_class_by_identifier_name(self,
                                               runtime_class: RuntimeClass,
                                               identifier_name: str,
                                               is_not_variable: bool = False,
                                               need_warning: bool = True
                                               ) -> RuntimeClass:
        """推断出现在当前类中标识符名称的类型

        Parameters
        ----------
        runtime_class : RuntimeClass
            运行中类对象
        identifier_name : str
            标识符名称
        is_not_variable : bool
            当前标识符是否一定不是变量
            之所以需要这个参数，是因为当类属性的变量名和类型相同时，如果没有这个参数会导致无限递归
        need_warning : bool
            如果匹配失败是否需要发送警告信息

        Returns
        -------

        """

        # 【场景】类的类型参数
        # - 抽象语法树节点为标识符类型（`Identifier`）
        # - 类的类型参数不为空
        # - 标识符的值与类的泛型的值相同
        if runtime_class is not None and runtime_class.type_arguments is not None:
            for idx, type_argument in enumerate(self.class_node.type_parameters):
                if isinstance(type_argument, ast.TypeParameter):
                    if type_argument.name == identifier_name:
                        return runtime_class.type_arguments[idx]
                else:
                    LOGGER.warning("未知泛型参数节点:", type_argument)

        # 【场景】类变量
        # - 标识符类型（`Identifier`）节点
        # - 标识符的值为类（或继承的父类、实现的接口）中的变量名称
        if is_not_variable is False:
            # 尝试性地寻找类变量，如果需要不到不需要报警，而是由 file_context.infer_runtime_class_by_identifier_name 报警
            variable_info = self.get_variable_node_by_name(identifier_name, need_warning=False)
            if variable_info is not None:
                class_context, variable_node = variable_info
                return class_context.infer_runtime_class_by_node(
                    runtime_class=class_context.get_runtime_class(),
                    type_node=variable_node.variable_type,
                    is_not_variable=True
                )

        return self.file_context.infer_runtime_class_by_identifier_name(
            identifier_name=identifier_name,
            need_warning=need_warning
        )
