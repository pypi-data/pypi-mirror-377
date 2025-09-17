import importlib
import inspect
from typing import List, Dict, Type, Any
import logging

class IntegrationDiscovery:
    """Automatically discover LangChain integrations with simplified approach"""
    
    def __init__(self, patterns: List[str] = None):
        self.patterns = patterns or [
            "langchain_*",
            "langchain.*",
            "*langchain*"
        ]
        self.logger = logging.getLogger(__name__)
        
    def discover_all_integrations(self) -> Dict[str, List[Type]]:
        """Discover all LangChain integrations by type"""
        discovered = {
            "llms": [],
            "chat_models": [],
            "embeddings": []
        }
        
        # Get base classes - try different import paths
        base_classes = self._get_base_classes()
        if not base_classes:
            self.logger.warning("Could not import base classes")
            return discovered
            
        BaseLLM, BaseChatModel, Embeddings = base_classes
        
        # Discover from third-party packages first (most reliable)
        third_party_result = self._discover_from_third_party(BaseLLM, BaseChatModel, Embeddings)
        for category, classes in third_party_result.items():
            discovered[category].extend(classes)
        
        # Try to discover from community packages if available
        try:
            community_result = self._discover_from_community_packages(BaseLLM, BaseChatModel, Embeddings)
            for category, classes in community_result.items():
                discovered[category].extend(classes)
        except Exception as e:
            self.logger.info(f"Community packages discovery failed: {e}")
        
        return discovered
    
    def discover_all(self) -> Dict[str, List[Type]]:
        """Alias for discover_all_integrations() for backward compatibility"""
        return self.discover_all_integrations()
    
    def _get_base_classes(self):
        """Get base classes with fallback imports"""
        try:
            # Try langchain_core first (newer approach)
            from langchain_core.language_models.llms import BaseLLM
            from langchain_core.language_models.chat_models import BaseChatModel
            from langchain_core.embeddings import Embeddings
            return BaseLLM, BaseChatModel, Embeddings
        except ImportError:
            try:
                # Fallback to langchain imports
                from langchain.llms.base import BaseLLM
                from langchain.chat_models.base import BaseChatModel
                from langchain.embeddings.base import Embeddings
                return BaseLLM, BaseChatModel, Embeddings
            except ImportError:
                self.logger.error("Could not import base classes from either langchain_core or langchain")
                return None
    
    def _discover_from_third_party(self, BaseLLM, BaseChatModel, Embeddings) -> Dict[str, List[Type]]:
        """Discover integrations from third-party packages"""
        integrations = {
            "llms": [],
            "chat_models": [],
            "embeddings": []
        }
        
        # Use configured patterns if available, otherwise use default known packages
        if self.patterns and any(pattern != "langchain_*" for pattern in self.patterns):
            # Use pattern-based discovery (for future extensibility)
            third_party_packages = self._get_packages_from_patterns()
        else:
            # List of known third-party LangChain integration packages
            third_party_packages = [
                "langchain_openai",
                "langchain_anthropic", 
                "langchain_google_genai",
                "langchain_aws",
                "langchain_cohere",
                "langchain_huggingface",
                "langchain_mlx",
                "langchain_google_vertexai",
                "langchain_together",
                "langchain_pinecone",
                "langchain_chroma",
                "langchain_weaviate"
            ]
        
        for package_name in third_party_packages:
            try:
                package = importlib.import_module(package_name)
                
                # Check root level for classes
                integrations["llms"].extend(self._find_classes_in_module(package, BaseLLM))
                integrations["chat_models"].extend(self._find_classes_in_module(package, BaseChatModel))
                integrations["embeddings"].extend(self._find_classes_in_module(package, Embeddings))
                
                self.logger.debug(f"Successfully scanned package {package_name}")
                
            except ImportError:
                self.logger.debug(f"Package {package_name} not available")
                continue
            except Exception as e:
                self.logger.warning(f"Error scanning package {package_name}: {e}")
                continue
                
        return integrations
    
    def _get_packages_from_patterns(self) -> List[str]:
        """Get package names based on patterns (placeholder for future pattern matching)"""
        # For now, return default packages, but this could be extended to use pkgutil.iter_modules
        # to find packages matching patterns
        return [
            "langchain_openai",
            "langchain_anthropic", 
            "langchain_google_genai",
            "langchain_aws",
            "langchain_cohere",
            "langchain_huggingface",
            "langchain_mlx",
            "langchain_google_vertexai"
        ]
    
    def _discover_from_community_packages(self, BaseLLM, BaseChatModel, Embeddings) -> Dict[str, List[Type]]:
        """Discover integrations from langchain-community package"""
        integrations = {
            "llms": [],
            "chat_models": [],
            "embeddings": []
        }
        
        try:
            # Try langchain-community package  
            import langchain_community  # noqa: F401
            
            # Try specific submodules with better error handling
            community_modules = [
                ("langchain_community.llms", "llms", BaseLLM),
                ("langchain_community.chat_models", "chat_models", BaseChatModel),
                ("langchain_community.embeddings", "embeddings", Embeddings)
            ]
            
            for module_name, category, base_class in community_modules:
                try:
                    module = importlib.import_module(module_name)
                    found_classes = self._find_classes_in_module(module, base_class)
                    integrations[category].extend(found_classes)
                    if found_classes:
                        self.logger.debug(f"Found {len(found_classes)} {category} in {module_name}")
                except ImportError as e:
                    self.logger.debug(f"Could not import {module_name}: {e}")
                except Exception as e:
                    self.logger.warning(f"Error scanning {module_name}: {e}")
                    
        except ImportError:
            self.logger.debug("langchain-community package not available")
            
        return integrations
    
    def _find_classes_in_module(self, module: Any, base_class: Type) -> List[Type]:
        """Find all classes in a module that inherit from base_class"""
        classes = []
        
        try:
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if self._is_valid_integration_class(obj, base_class, module):
                    classes.append(obj)
                    self.logger.debug(f"Found {name} ({obj.__name__}) in {module.__name__}")
                    
        except Exception as e:
            self.logger.warning(f"Error scanning module {module}: {e}")
            
        return classes
    
    def _is_valid_integration_class(self, obj: Type, base_class: Type, module: Any) -> bool:
        """Check if a class is a valid integration class"""
        try:
            return (
                issubclass(obj, base_class) and 
                obj != base_class and
                not inspect.isabstract(obj) and
                obj.__module__.startswith(module.__name__) and
                not obj.__name__.startswith('_') and
                not obj.__name__.startswith('Base')
            )
        except TypeError:
            # Handle cases where issubclass fails
            return False
    
    def get_integration_info(self, integration_class: Type) -> Dict[str, Any]:
        """Get detailed information about an integration"""
        info = {
            "name": integration_class.__name__,
            "module": integration_class.__module__,
            "version": getattr(integration_class, "__version__", "unknown"),
            "doc": integration_class.__doc__ or "",
            "methods": [],
            "required_params": [],
            "optional_params": []
        }
        
        # Get method information (both functions and methods)
        for name, method in inspect.getmembers(integration_class):
            if (callable(method) and 
                not name.startswith('_') and 
                not name in ['__class__', '__dict__', '__doc__', '__module__']):
                info["methods"].append(name)
        
        # Get constructor parameters
        try:
            sig = inspect.signature(integration_class.__init__)
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                if param.default == inspect.Parameter.empty:
                    info["required_params"].append(param_name)
                else:
                    info["optional_params"].append(param_name)
                    
        except Exception as e:
            self.logger.warning(f"Could not inspect constructor for {integration_class.__name__}: {e}")
            
        return info