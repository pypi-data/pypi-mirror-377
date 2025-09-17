"""
上下文管理器的抽象基类
"""

import abc
from typing import Dict, Generator, List, Optional, Tuple, Type

from metasequoia_java import ast
from metasequoia_java.sa.elements import RuntimeClass
from metasequoia_java.sa.elements import RuntimeMethod
from metasequoia_java.sa.elements import RuntimeVariable
from metasequoia_java.sa.name_space import NameSpace
from metasequoia_java.sa.name_space import SimpleNameSpace

__all__ = [
    "ProjectContext",
    "FileContext",
    "ClassContext",
    "MethodContext",
]


class ProjectContext(abc.ABC):
    """项目层级消上下文管理器的抽象基类"""

    @property
    @abc.abstractmethod
    def project_path(self) -> str:
        """返回项目根路径"""

    # ------------------------------ package 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_package_path_list_by_package_name(self, package_name: Optional[str]) -> List[str]:
        """根据 package_name 获取所有可能的 package_path 的列表"""

    @abc.abstractmethod
    def get_file_path_list_by_package_name(self, package_name: str) -> List[str]:
        """根据 package_name 获取其中所有文件的文件路径的列表"""

    @abc.abstractmethod
    def get_class_name_list_by_package_name(self, package_name: str) -> List[str]:
        """根据 package_name（包名称）获取其中所有模块内可见类的 class_name（类名）的列表"""

    @abc.abstractmethod
    def get_static_variable_name_list_by_runtime_class(self, runtime_class: RuntimeClass) -> Optional[List[str]]:
        """根据 runtimeClass 对象获取该对象中静态变量名称的列表"""

    @abc.abstractmethod
    def get_static_method_name_list_by_runtime_class(self, runtime_class: RuntimeClass) -> Optional[List[str]]:
        """根据 runtimeClass 对象获取该对象中静态方法名称的列表"""

    # ------------------------------ file 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_file_node_by_file_path(self, file_path: str) -> ast.CompilationUnit:
        """根据 file_path（文件路径）获取 file_node（抽象语法树的文件节点）"""

    @abc.abstractmethod
    def get_file_path_by_package_name_class_name(self,
                                                 package_name: str,
                                                 public_class_name: str,
                                                 need_warning: bool = True
                                                 ) -> Optional[str]:
        """根据 package_name 和公有类的 class_name 获取对应文件的绝对路径"""

    @abc.abstractmethod
    def get_file_node_by_package_name_class_name(self,
                                                 package_name: str,
                                                 public_class_name: str,
                                                 need_warning: bool = True
                                                 ) -> Optional[ast.CompilationUnit]:
        """根据 package_name 和公有类的 class_name 获取对应文件的抽象语法树节点"""

    # ------------------------------ 项目全局搜索方法 ------------------------------

    @abc.abstractmethod
    def create_file_context_by_runtime_class(self,
                                             runtime_class: Optional[RuntimeClass],
                                             need_warning: bool = True
                                             ) -> Optional["FileContext"]:
        """尝试根据 RuntimeClass 对象构造公有类所在文件的 FileContext 对象，如果在当前项目中查找不到 RuntimeClass 则返回 None"""

    @abc.abstractmethod
    def create_class_context_by_runtime_class(self,
                                              runtime_class: Optional[RuntimeClass],
                                              need_warning: bool = True
                                              ) -> Optional["ClassContext"]:
        """尝试根据 RuntimeClass 构造 ClassContext 对象，如果在当前项目中查找不到 RuntimeClass 则返回 None"""

    @abc.abstractmethod
    def create_method_context_by_runtime_method(self,
                                                runtime_method: Optional[RuntimeMethod],
                                                need_warning: bool = True) -> Optional["MethodContext"]:
        """根据 runtimeMethod 对象构造 MethodContext 对象，如果不在当前项目中则返回 None"""

    @abc.abstractmethod
    def get_type_runtime_class_by_runtime_variable(self, runtime_variable: RuntimeVariable) -> Optional[RuntimeClass]:
        """根据 runtimeVariable 返回值的类型，构造 runtimeClass"""

    @abc.abstractmethod
    def get_variable_info_by_runtime_variable(self,
                                              runtime_variable: RuntimeVariable,
                                              need_warning: bool = True
                                              ) -> Optional[Tuple["ClassContext", ast.Variable]]:
        """根据 RuntimeVariable 对象获取该变量所在类的 ClassContext 对象，以及初始化该对象的抽象语法树节点"""

    @abc.abstractmethod
    def get_runtime_class_by_runtime_method_param(self,
                                                  runtime_method: RuntimeMethod,
                                                  param_idx: int
                                                  ) -> Optional[RuntimeClass]:
        """根据 RuntimeMethod 对象，返回其中第 param_idx 个参数的类型"""

    @abc.abstractmethod
    def get_runtime_class_by_runtime_method_return_type(self, runtime_method: RuntimeMethod) -> Optional[RuntimeClass]:
        """根据 runtimeMethod 返回值的类型，构造 runtimeClass"""

    @abc.abstractmethod
    def get_runtime_class_list_by_functional_interface(self, runtime_class: RuntimeClass
                                                       ) -> Optional[List[RuntimeClass]]:
        """根据函数式接口 RuntimeClass 的 lambda 表达式的参数类型列表"""

    # ------------------------------ 项目外已知信息管理方法 ------------------------------

    @abc.abstractmethod
    def try_get_outer_attribute_type(self, runtime_variable: RuntimeVariable) -> Optional[RuntimeClass]:
        """获取项目外已知类属性类型"""

    @abc.abstractmethod
    def try_get_outer_method_param_type(self, runtime_method: RuntimeMethod, param_idx: int) -> Optional[RuntimeClass]:
        """获取项目外已知方法参数类型"""

    @abc.abstractmethod
    def try_get_outer_method_return_type(self, runtime_method: RuntimeMethod) -> Optional[RuntimeClass]:
        """获取项目外已知方法返回值类型"""

    @abc.abstractmethod
    def try_get_outer_package_class_name_list(self, package_name: str) -> Optional[List[str]]:
        """获取项目外 package_name 对应的 class_name 的列表"""

    @abc.abstractmethod
    def try_get_runtime_class_list_by_functional_interface(self, runtime_class: RuntimeClass
                                                           ) -> Optional[List[RuntimeClass]]:
        """获取项目外的函数式接口 RuntimeClass 的 lambda 表达式的参数类型列表"""


class FileContext(abc.ABC):
    """文件层级上下文管理器的抽象基类"""

    @property
    @abc.abstractmethod
    def project_context(self) -> ProjectContext:
        """返回所属项目上下文管理器"""

    @property
    @abc.abstractmethod
    def package_name(self) -> str:
        """返回所属 package 名称"""

    @property
    @abc.abstractmethod
    def public_class_name(self) -> str:
        """返回文件中的公有类名称"""

    @property
    @abc.abstractmethod
    def file_node(self) -> ast.CompilationUnit:
        """返回文件的抽象语法树节点"""

    @property
    @abc.abstractmethod
    def import_class_hash(self) -> Dict[str, RuntimeClass]:
        """返回类引用映射"""

    @property
    @abc.abstractmethod
    def import_variable_hash(self) -> Dict[str, RuntimeVariable]:
        """返回静态属性引用映射"""

    @property
    @abc.abstractmethod
    def import_method_hash(self) -> Dict[str, RuntimeMethod]:
        """返回静态方法引用映射"""

    # ------------------------------ 元素类型推断 ------------------------------

    @abc.abstractmethod
    def import_contains_class_name(self, class_name: str) -> bool:
        """返回引用映射中是否包含类型"""

    @abc.abstractmethod
    def infer_runtime_class_by_identifier_name(self,
                                               identifier_name: str,
                                               need_warning: bool = True) -> Optional[RuntimeClass]:
        """根据当前文件中出现的 class_name，获取对应的 RuntimeClass 对象"""

    @abc.abstractmethod
    def infer_runtime_class_by_node(self, type_node: ast.Tree) -> Optional[RuntimeClass]:
        """推断当前文件中出现的抽象语法树节点的类型"""


class ClassContext(abc.ABC):
    """类层级上下文管理器的抽象基类"""

    @property
    @abc.abstractmethod
    def project_context(self) -> ProjectContext:
        """返回所属项目上下文管理器"""

    @property
    @abc.abstractmethod
    def file_context(self) -> FileContext:
        """返回所属文件上下文管理器"""

    @property
    @abc.abstractmethod
    def class_name(self) -> str:
        """返回类名"""

    @property
    @abc.abstractmethod
    def class_node(self) -> ast.Class:
        """返回类的抽象语法树节点"""

    @property
    @abc.abstractmethod
    def outer_class_context(self) -> Optional["ClassContext"]:
        """返回外部类的 ClassContext 对象（仅当当前类为内部类时不为 None）"""

    # ------------------------------ method 和 variable 层级处理方法 ------------------------------

    @abc.abstractmethod
    def get_method_node_by_name(self, method_name: str) -> Optional[Tuple["ClassContext", ast.Method]]:
        """根据 method_name 获取方法的抽象语法树节点"""

    @abc.abstractmethod
    def get_variable_node_by_name(self, variable_name: str) -> Optional[Tuple["ClassContext", ast.Variable]]:
        """根据 variable_name 获取类变量的抽象语法树节点"""

    @abc.abstractmethod
    def get_extends_and_implements(self) -> List[RuntimeClass]:
        """获取继承和实现接口的类的 RuntimeClass 对象的列表"""

    @abc.abstractmethod
    def get_runtime_class(self) -> RuntimeClass:
        """构造当前类上下文对应的 RuntimeClass 对象"""

    # ------------------------------ 命名空间管理器 ------------------------------

    @abc.abstractmethod
    def get_simple_name_space(self) -> SimpleNameSpace:
        """返回类变量的单层命名空间"""

    @abc.abstractmethod
    def get_name_space(self) -> NameSpace:
        """返回包含类变量的命名空间"""

    # ------------------------------ 元素类型推断 ------------------------------

    @abc.abstractmethod
    def infer_runtime_class_by_node(self,
                                    runtime_class: RuntimeClass,
                                    type_node: ast.Tree,
                                    is_not_variable: bool = False
                                    ) -> Optional[RuntimeClass]:
        """推断出现在当前类中的抽象语法树类型"""

    @abc.abstractmethod
    def infer_runtime_class_by_identifier_name(self,
                                               runtime_class: RuntimeClass,
                                               identifier_name: str,
                                               is_not_variable: bool = False,
                                               need_warning: bool = True
                                               ) -> RuntimeClass:
        """推断出现在当前类中标识符名称的类型"""


class MethodContext(abc.ABC):
    """方法层级上下文管理器的抽象基类"""

    @property
    @abc.abstractmethod
    def project_context(self) -> ProjectContext:
        """返回所属的项目上下文管理器"""

    @property
    @abc.abstractmethod
    def file_context(self) -> FileContext:
        """返回所属的文件上下文管理器"""

    @property
    @abc.abstractmethod
    def class_context(self) -> ClassContext:
        """返回所属的类上下文管理器"""

    @property
    @abc.abstractmethod
    def method_name(self) -> str:
        """返回方法名称"""

    @property
    @abc.abstractmethod
    def method_node(self) -> ast.Method:
        """返回方法的抽象语法树节点"""

    @abc.abstractmethod
    def get_runtime_method(self) -> RuntimeMethod:
        """返回当前方法上下文对应的 RuntimeMethod 对象"""

    # ------------------------------ 命名空间管理器 ------------------------------

    @abc.abstractmethod
    def get_name_space(self) -> NameSpace:
        """返回包含类变量、方法参数变量和方法代码块中变量的命名空间"""

    # ------------------------------ 抽象语法树遍历器 ------------------------------

    @abc.abstractmethod
    def get_method_invocation(self,
                              runtime_method: RuntimeMethod,
                              namespace: NameSpace,
                              statement_node: ast.Tree,
                              outer_runtime_method: Optional[RuntimeMethod] = None,
                              outer_method_param_idx: Optional[int] = None
                              ) -> Generator[Tuple[RuntimeMethod, ast.MethodInvocation], None, None]:
        """获取当前表达式中调用的方法"""

    @abc.abstractmethod
    def visitor_tree(self,
                     runtime_method: RuntimeMethod,
                     namespace: NameSpace,
                     ast_node: ast.Tree,
                     outer_runtime_method: Optional[RuntimeMethod] = None,
                     outer_method_param_idx: Optional[int] = None
                     ) -> Generator[Tuple[NameSpace, ast.Tree], None, None]:
        """遍历抽象语法树中的所有节点

        Parameters
        ----------
        runtime_method : RuntimeMethod
            当前方法所在的方法上下文管理器
        namespace : NameSpace
            当前方法所在位置的命名空间
        ast_node : ast.Tree
            待分析的抽象语法树节点
        outer_runtime_method : Optional[RuntimeClass], default = None
            如果当前抽象语法树节点为某个方法的参数，则为调用包含该参数的外层方法的 RuntimeMethod 对象，用于实现 lambda 语句的类型推断
        outer_method_param_idx : Optional[int], default = None
            如果当前抽象语法树节点为某个方法的参数，则为调用包含该参数的外层方法的参数下标，用于实现 lambda 语句的类型推断
        """

    @abc.abstractmethod
    def search_node(self,
                    statement_node: ast.Tree,
                    search_type: Type,
                    ) -> Generator[ast.Tree, None, None]:
        """获取当前表达式中调用的方法中，寻找 search_type 类型的节点"""

    # ------------------------------ 元素类型推断 ------------------------------

    @abc.abstractmethod
    def infer_runtime_class_by_node(self,
                                    runtime_method: RuntimeMethod,
                                    namespace: NameSpace,
                                    type_node: ast.Tree
                                    ) -> Optional[RuntimeClass]:
        """推断出现在当前方法中的抽象语法树类型"""

    @abc.abstractmethod
    def infer_runtime_class_by_identifier_name(self,
                                               runtime_method: RuntimeMethod,
                                               namespace: NameSpace,
                                               identifier_name: str,
                                               need_warning: bool = True
                                               ) -> RuntimeClass:
        """推断出现在当前方法中标识符名称的类型"""
