
from pydantic import BaseModel
from typing import Literal, Optional, List, Any, Union
from typing import get_origin, get_args
from typing import Type
from pydantic_core import PydanticUndefined
import annotated_types


def is_literal_or_optional(type_hint: Type) -> str:
    """
    判断类型是否是 Literal 或 Optional 类型，返回类型的名称。
    """
    origin = get_origin(type_hint)  # 获取类型的原始类型
    args = get_args(type_hint)      # 获取类型的参数
    # print(f"{type_hint} : {origin} : {args}")
    # 检查是否是 Optional
    if origin is Union and len(args) == 2 and args[1] is type(None):
        return args[0].__name__
    # Optional[str]

    if origin is Union and len(args) == 1:
        return type(args[0]).__name__
    # 检查是否是 Literal
    if origin is Literal:
        return type(args[0]).__name__
    if origin is list:
        return f"{origin.__name__}[{args[0].__name__}]"
    return type_hint.__name__

def generate_metadata(model_class: BaseModel) -> List[dict]:
    metadata = []
    # 遍历模型的字段
    annotations = {**model_class.__annotations__}
    for field_name, field in annotations.items():
        if field_name == "model":
            continue
        field_info = model_class.model_fields[field_name]
        # print("****************************")
        field_type = is_literal_or_optional(field_info.annotation)
        # 准备字段元数据
        # print(f"field_name : {field_name}: field_info.annotation : {field_info.annotation}, field_type: {field_type}")
        # if field_info.annotation in (Literal, Union):
        #     print(type(field_type.__args__[0]).__name__) 
        field_metadata = {
            "key": field_name,
            "label": field_info.title,  # 使用 'label' 字段，默认使用字段名
            "type": field_type,
            "default": field_info.default if field_info.default is not PydanticUndefined else (0 if field_type == "int" else ""),
            "placeholder": field_info.description,
            "component": field_info.json_schema_extra.get("type", "input") if field_info.json_schema_extra else "input",
            "value": field_info.json_schema_extra.get("value", "") if field_info.json_schema_extra else "",
            "required": field_info.is_required(),
        }

        constraints = {}
        for item in field_info.metadata:
            if isinstance(item, annotated_types.Ge):
                constraints['min'] = field_info.metadata[0].ge
            elif isinstance(item, annotated_types.Le):
                constraints['max'] = field_info.metadata[1].le

        limit = {}
        if "list" in field_metadata["type"]:
            print("hh" + field_info.json_schema_extra)
            field_metadata["max_length"] = field_info.json_schema_extra.get("max_length", 1) if field_info.json_schema_extra else 0,
        if constraints:
            field_metadata.update(constraints)

        metadata.append(field_metadata)

    return metadata
