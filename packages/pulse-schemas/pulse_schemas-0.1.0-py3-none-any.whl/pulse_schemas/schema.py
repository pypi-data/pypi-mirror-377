from typing import List, Optional, Dict, Type
from pydantic import BaseModel
from typing_extensions import Literal


# ------------------------
# Step 1: Define Schemas
# ------------------------

class Demographics(BaseModel):
    age: Optional[int]
    biological_sex: Optional[
        Literal["male", "female", "other", "prefer_not_to_say"]
    ]


class ProfileSchema(BaseModel):
    demographics: Optional[Demographics]
    dietary_preferences: List[
        Literal[
            "vegan", "vegetarian", "pescatarian",
            "keto", "paleo", "halal", "kosher", "none"
        ]
    ]
    allergens: List[
        Literal[
            "peanuts", "tree nuts", "milk", "eggs",
            "fish", "shellfish", "soy", "wheat",
            "sesame", "gluten", "dairy", "latex", "other allergen"
        ]
    ]
    health_conditions: List[
        Literal[
            "diabetes", "hypertension", "heart disease",
            "high blood pressure", "cardiovascular disease",
            "respiratory condition", "other health conditions"
        ]
    ]
    goals: List[Literal["lose weight", "build muscle", "improve cardio"]]


# ------------------------
# Step 2: Schema Manager
# ------------------------

class SchemaRegistry:
    """Registry for storing and retrieving Pydantic schemas."""

    def __init__(self):
        self._schemas: Dict[str, Type[BaseModel]] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register built-in schemas."""
        self.register_schema("create_user_profile", ProfileSchema)

    def register_schema(self, name: str, schema: Type[BaseModel]):
        """Register a new schema."""
        self._schemas[name] = schema

    def get_schema(self, name: str) -> Optional[Type[BaseModel]]:
        """Retrieve a schema by name."""
        return self._schemas.get(name)

    def list_schemas(self) -> List[str]:
        """List all available schema names."""
        return list(self._schemas.keys())
