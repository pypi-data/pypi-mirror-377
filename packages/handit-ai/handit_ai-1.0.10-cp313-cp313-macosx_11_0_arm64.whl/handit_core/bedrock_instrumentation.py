"""Amazon Bedrock instrumentation to capture high-level API calls."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

try:
    from . import handit_core_native as _native  # type: ignore
except Exception:  # pragma: no cover
    _native = None  # type: ignore

from . import _active_session_id  # type: ignore

import json, dataclasses, base64
from decimal import Decimal
from uuid import UUID
from datetime import date, datetime

def to_jsonable(x, _depth=0, _seen=None):
    """Convert objects to JSON-serializable format, handling Bedrock-specific types."""
    
    # Prevent infinite recursion with depth limit and circular reference detection
    if _depth > 10:  # Max recursion depth
        try:
            if hasattr(x, 'content') and x.content:
                return f"<max-depth-reached-content: {x.content}>"
            elif hasattr(x, 'text') and x.text:
                return f"<max-depth-reached-text: {x.text}>"
            elif hasattr(x, 'message') and x.message:
                return f"<max-depth-reached-message: {x.message}>"
            else:
                return f"<max-depth-reached: {str(x)}>"
        except:
            return "<max-depth-reached>"
    
    if _seen is None:
        _seen = set()
    
    # Check for circular references
    obj_id = id(x)
    if obj_id in _seen:
        try:
            if hasattr(x, 'content') and x.content:
                return f"<circular-ref-content: {x.content}>"
            elif hasattr(x, 'text') and x.text:
                return f"<circular-ref-text: {x.text}>"
            elif hasattr(x, 'message') and x.message:
                return f"<circular-ref-message: {x.message}>"
            else:
                return f"<circular-ref: {str(x)[:500]}>"
        except:
            return "<circular-reference>"
    
    # Handle None first
    if x is None:
        return None
    
    # Built-ins (fast path) - no need to track these in _seen
    if isinstance(x, (str, int, float, bool)):
        return x
    
    # Add to seen set for circular reference detection
    _seen.add(obj_id)
    
    # Handle AWS SDK response objects
    if hasattr(x, "get"):
        try:
            return dict(x)
        except Exception:
            pass
    
    # Pydantic v2 (AWS SDK v2+)
    if hasattr(x, "model_dump"):
        try:
            return x.model_dump(exclude_unset=True)
        except Exception:
            try:
                return x.model_dump()
            except Exception:
                pass
    
    # Pydantic v1 / common libs
    if hasattr(x, "dict"):
        try:
            return x.dict()
        except Exception:
            pass
    
    # Dataclasses
    if dataclasses.is_dataclass(x):
        try:
            return dataclasses.asdict(x)
        except Exception:
            pass
    
    # Collections - pass depth and seen set to prevent infinite recursion
    if isinstance(x, (list, tuple, set, frozenset)):
        try:
            return [to_jsonable(v, _depth + 1, _seen) for v in x]
        except Exception:
            return [str(v) for v in x]
    
    if isinstance(x, dict):
        try:
            return {str(k): to_jsonable(v, _depth + 1, _seen) for k, v in x.items()}
        except Exception:
            return {str(k): str(v) for k, v in x.items()}
    
    # Common non-JSON types
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    if isinstance(x, (UUID, Decimal)):
        return str(x)
    if isinstance(x, (bytes, bytearray)):
        return base64.b64encode(x).decode("utf-8")
    
    # Last resort with error handling
    if hasattr(x, "__dict__"):
        try:
            return {k: to_jsonable(v, _depth + 1, _seen) for k, v in vars(x).items()}
        except Exception:
            try:
                important_data = {}
                for attr in ['content', 'text', 'message', 'data', 'response', 'body']:
                    if hasattr(x, attr):
                        val = getattr(x, attr)
                        if val:
                            important_data[attr] = str(val)[:1000]  # Capture first 1000 chars
                if important_data:
                    return important_data
                else:
                    return {"<serialization-error>": str(x)[:500]}
            except:
                return {"<serialization-error>": str(x)[:500]}
    
    # Final fallback
    return str(x)

def to_json_string(obj) -> str:
    """Convert object to JSON string."""
    return json.dumps(to_jsonable(obj, _depth=0, _seen=None), ensure_ascii=False, separators=(",", ":"))

def patch_bedrock() -> None:
    """Patch Amazon Bedrock to emit custom events for API calls"""
    try:
        import boto3
        from botocore.client import BaseClient
    except Exception:
        return
    
    # Patch the boto3.client function to intercept bedrock-runtime clients
    if hasattr(boto3.client, '_handit_patched'):
        return
    
    orig_boto3_client = boto3.client
    
    def wrapped_boto3_client(service_name, **kwargs):
        """Wrapped boto3.client that patches bedrock-runtime clients"""
        client = orig_boto3_client(service_name, **kwargs)
        
        # Only patch bedrock-runtime clients
        if service_name == 'bedrock-runtime':
            _patch_bedrock_client(client)
        
        return client
    
    # Mark as patched and replace
    wrapped_boto3_client._handit_patched = True
    wrapped_boto3_client._handit_orig = orig_boto3_client
    boto3.client = wrapped_boto3_client
    
    # Also patch any existing boto3.client instances that might have been created before patching
    _patch_existing_bedrock_clients()

def _patch_bedrock_client(client):
    """Patch a specific Bedrock client instance"""
    # Prevent double patching
    if hasattr(client, '_handit_bedrock_patched'):
        return
    
    # Get the original methods
    orig_invoke_model = client.invoke_model
    orig_invoke_model_with_response_stream = getattr(client, 'invoke_model_with_response_stream', None)
    
    def wrapped_invoke_model(**kwargs):  # type: ignore[no-untyped-def]
        model_id = kwargs.get("modelId", "unknown")
        body = kwargs.get("body", {})
        content_type = kwargs.get("contentType", "application/json")
        
        # Extract other params for logging
        other_params = {k: v for k, v in kwargs.items() if k not in ["modelId", "body", "contentType"]}
        params = {
            "modelId": model_id,
            "body": body,
            "contentType": content_type,
            **other_params
        }
        
        # Emit call event
        _native_on = getattr(_native, "on_call_with_args_py", None)
        _return_on = getattr(_native, "on_return_with_preview_py", None)
        if _native_on is None or _return_on is None:
            return orig_invoke_model(**kwargs)
        
        sid = _active_session_id.get()
        if not sid or _native is None:
            return orig_invoke_model(**kwargs)
        
        func_name = "invoke_model"
        module_name = "boto3.client.bedrock-runtime"
        file_name = "<bedrock-api>"
        line_no = 1
        t0 = time.time_ns()

        params_json = to_json_string(params)
        _native_on(sid, func_name, module_name, file_name, line_no, t0, params_json)
        
        # Suppress profiler during Bedrock call
        _suppress_enter = getattr(_native, "suppress_profiler_enter_py", None)
        _suppress_exit = getattr(_native, "suppress_profiler_exit_py", None)
        if callable(_suppress_enter):
            try:
                _suppress_enter()
            except Exception:
                pass
        
        try:
            # Make the actual call
            result = orig_invoke_model(**kwargs)
            
            # Emit return event with safe serialization
            t1 = time.time_ns()
            dt_ns = t1 - t0
            
            # Extract essential Bedrock response data
            try:
                response_data = {
                    "statusCode": getattr(result, 'ResponseMetadata', {}).get('HTTPStatusCode', None),
                    "contentType": result.get('contentType', None),
                    "body": result.get('body', None)
                }
                
                # Try to parse body if it's bytes
                if isinstance(response_data["body"], bytes):
                    try:
                        body_str = response_data["body"].decode('utf-8')
                        response_data["body"] = json.loads(body_str)
                    except:
                        response_data["body"] = "<binary-data>"
                
                result_json = json.dumps(response_data, ensure_ascii=False, separators=(",", ":"))
                    
            except Exception as serialize_error:
                # Fallback - just get basic info
                try:
                    result_json = f"{{\"statusCode\": {getattr(result, 'ResponseMetadata', {}).get('HTTPStatusCode', 'unknown')}, \"extraction_method\": \"fallback\"}}"
                except Exception:
                    result_json = f"{{\"error\": \"Failed to extract Bedrock response data\"}}"
            
            _return_on(sid, func_name, t1, dt_ns, result_json)
            
            return result
            
        except Exception as e:
            # Emit return event for exceptions too
            t1 = time.time_ns()
            dt_ns = t1 - t0
            error_json = f"{{\"error\": \"{str(e)[:500]}\"}}"
            try:
                _return_on(sid, func_name, t1, dt_ns, error_json)
            except:
                pass  # Don't let logging errors break the original exception
            raise
        finally:
            # Always restore profiler suppression
            if callable(_suppress_exit):
                try:
                    _suppress_exit()
                except Exception:
                    pass
    
    def wrapped_invoke_model_with_response_stream(**kwargs):  # type: ignore[no-untyped-def]
        model_id = kwargs.get("modelId", "unknown")
        body = kwargs.get("body", {})
        content_type = kwargs.get("contentType", "application/json")
        
        # Extract other params for logging
        other_params = {k: v for k, v in kwargs.items() if k not in ["modelId", "body", "contentType"]}
        params = {
            "modelId": model_id,
            "body": body,
            "contentType": content_type,
            **other_params
        }
        
        # Emit call event
        _native_on = getattr(_native, "on_call_with_args_py", None)
        _return_on = getattr(_native, "on_return_with_preview_py", None)
        if _native_on is None or _return_on is None:
            return orig_invoke_model_with_response_stream(**kwargs)
        
        sid = _active_session_id.get()
        if not sid or _native is None:
            return orig_invoke_model_with_response_stream(**kwargs)
        
        func_name = "invoke_model_with_response_stream"
        module_name = "boto3.client.bedrock-runtime"
        file_name = "<bedrock-api>"
        line_no = 1
        t0 = time.time_ns()

        params_json = to_json_string(params)
        _native_on(sid, func_name, module_name, file_name, line_no, t0, params_json)
        
        # Suppress profiler during Bedrock call
        _suppress_enter = getattr(_native, "suppress_profiler_enter_py", None)
        _suppress_exit = getattr(_native, "suppress_profiler_exit_py", None)
        if callable(_suppress_enter):
            try:
                _suppress_enter()
            except Exception:
                pass
        
        try:
            # Make the actual call
            result = orig_invoke_model_with_response_stream(**kwargs)
            
            # Emit return event with safe serialization
            t1 = time.time_ns()
            dt_ns = t1 - t0
            
            # For streaming responses, we can't easily capture the full response
            # So we'll just indicate it's a streaming response
            response_data = {
                "statusCode": getattr(result, 'ResponseMetadata', {}).get('HTTPStatusCode', None),
                "contentType": result.get('contentType', None),
                "body": "<streaming-response>"
            }
            
            result_json = json.dumps(response_data, ensure_ascii=False, separators=(",", ":"))
            _return_on(sid, func_name, t1, dt_ns, result_json)
            
            return result
            
        except Exception as e:
            # Emit return event for exceptions too
            t1 = time.time_ns()
            dt_ns = t1 - t0
            error_json = f"{{\"error\": \"{str(e)[:500]}\"}}"
            try:
                _return_on(sid, func_name, t1, dt_ns, error_json)
            except:
                pass  # Don't let logging errors break the original exception
            raise
        finally:
            # Always restore profiler suppression
            if callable(_suppress_exit):
                try:
                    _suppress_exit()
                except Exception:
                    pass
    
    # Apply patches to the client instance
    setattr(wrapped_invoke_model, "_handit_patched", True)
    setattr(wrapped_invoke_model, "_handit_orig", orig_invoke_model)
    client.invoke_model = wrapped_invoke_model  # type: ignore
    
    if orig_invoke_model_with_response_stream:
        setattr(wrapped_invoke_model_with_response_stream, "_handit_patched", True)
        setattr(wrapped_invoke_model_with_response_stream, "_handit_orig", orig_invoke_model_with_response_stream)
        client.invoke_model_with_response_stream = wrapped_invoke_model_with_response_stream  # type: ignore
    
    # Mark this client as patched
    client._handit_bedrock_patched = True

def _patch_existing_bedrock_clients():
    """Patch any existing boto3.client instances that were created before patching"""
    try:
        import boto3
        import gc
        
        # Get all objects in memory
        for obj in gc.get_objects():
            try:
                # Check if it's a boto3 client instance
                if (hasattr(obj, '__class__') and 
                    hasattr(obj, '_service_model') and
                    hasattr(obj, 'invoke_model')):
                    
                    # Check if it's a bedrock-runtime client
                    if (hasattr(obj._service_model, 'service_name') and 
                        obj._service_model.service_name == 'bedrock-runtime'):
                        
                        # This is a bedrock-runtime client, patch it
                        _patch_bedrock_client(obj)
                        
            except Exception:
                # Skip objects that cause errors when accessing attributes
                continue
                    
    except Exception:
        # If anything goes wrong, just continue
        pass

def patch_bedrock_client_for_langchain():
    """Patch LangChain Bedrock models when they are imported"""
    
    # Strategy: Patch the module import system to catch LangChain Bedrock models when imported
    import sys
    import importlib.util
    
    # Store original import
    original_import = __builtins__['__import__']
    
    def traced_import(name, globals=None, locals=None, fromlist=(), level=0):
        """Custom import that patches LangChain Bedrock models as they're imported"""
        
        # Call original import first
        module = original_import(name, globals, locals, fromlist, level)
        
        # Check if this is a LangChain Bedrock model import
        if name == 'langchain_aws' or (fromlist and 'ChatBedrock' in fromlist):
            try:
                from langchain_aws import ChatBedrock
                if not hasattr(ChatBedrock, '_handit_patched'):
                    _patch_chatbedrock()
            except:
                pass
        
        return module
    
    # Apply the import hook
    __builtins__['__import__'] = traced_import

def _patch_chatbedrock():
    """Actually patch ChatBedrock.ainvoke"""
    try:
        from langchain_aws import ChatBedrock
        
        original_ainvoke = ChatBedrock.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            """Traced ChatBedrock.ainvoke"""
            model_id = getattr(self, 'model_id', getattr(self, 'model', 'anthropic.claude-3-sonnet-20240229-v1:0'))
            
            # Convert input to messages
            if hasattr(input, '__iter__') and not isinstance(input, str):
                messages = list(input)
            else:
                messages = [{"role": "user", "content": str(input)}]
            
            t0_ns = _emit_bedrock_call("ChatBedrock.ainvoke", model_id, messages, **kwargs)
            
            try:
                result = await original_ainvoke(self, input, config, **kwargs)
                _emit_bedrock_return(t0_ns, "ChatBedrock.ainvoke", result)
                return result
            except Exception as error:
                _emit_bedrock_return(t0_ns, "ChatBedrock.ainvoke", None, str(error))
                raise
        
        ChatBedrock.ainvoke = traced_ainvoke
        ChatBedrock._handit_patched = True
        
    except Exception as e:
        pass

def _emit_bedrock_call(func_name: str, model_id: str, messages: list, **kwargs) -> int:
    """Emit Bedrock call event"""
    try:
        sid = _active_session_id.get()
        if not sid or _native is None:
            return 0
        
        t0_ns = time.time_ns()
        
        # Build args preview
        args_preview = {
            "model_id": model_id,
            "messages": messages,
            **kwargs
        }
        
        args_json = to_json_string(args_preview)
        
        _native_on = getattr(_native, "on_call_with_args_py", None)
        if _native_on:
            _native_on(sid, func_name, "langchain_aws", "<langchain-bedrock>", 1, t0_ns, args_json)
        
        return t0_ns
    except Exception:
        return 0

def _emit_bedrock_return(t0_ns: int, func_name: str, result: Any, error: Optional[str] = None) -> None:
    """Emit Bedrock return event"""
    try:
        sid = _active_session_id.get()
        if not sid or _native is None:
            return
        
        t1_ns = time.time_ns()
        dt_ns = t1_ns - t0_ns
        
        if error:
            result_json = f"{{\"error\": \"{error}\"}}"
        else:
            # Extract essential result data
            try:
                if hasattr(result, 'content'):
                    content = result.content
                elif hasattr(result, 'text'):
                    content = result.text
                else:
                    content = str(result)
                
                result_data = {
                    "content": content,
                    "model_id": getattr(result, 'model_id', None),
                    "usage": getattr(result, 'usage_metadata', None)
                }
                
                result_json = json.dumps(result_data, ensure_ascii=False, separators=(",", ":"))
            except Exception:
                result_json = f"{{\"content\": \"{str(result)[:500]}\"}}"
        
        _return_on = getattr(_native, "on_return_with_preview_py", None)
        if _return_on:
            _return_on(sid, func_name, t1_ns, dt_ns, result_json)
            
    except Exception:
        pass
