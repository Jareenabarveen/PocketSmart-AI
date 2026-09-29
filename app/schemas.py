from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    city: str = Field(default="Chennai", min_length=2, max_length=80)
    style: str = Field(default="modern", min_length=2, max_length=40)
    rooms: list[str] = Field(default_factory=lambda: ["Living Room"])
    items: dict[str, int] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=1000)

    @field_validator("items")
    @classmethod
    def validate_items(cls, value):
        for key, qty in value.items():
            if qty < 0 or qty > 50:
                raise ValueError(f"Invalid quantity for {key}")
        return value


class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    city: str = Field(default="Chennai", min_length=2, max_length=80)
    event_type: str = Field(default="birthday", min_length=2, max_length=40)
    guests: int = Field(gt=0, le=5000)
    venue: str = Field(default="home", min_length=2, max_length=80)
    date: str = Field(default="")
    notes: str = Field(default="", max_length=1000)


class RecommendationItem(BaseModel):
    title: str
    category: str
    platform: str
    price: float
    url: str
    reason: str


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    planner: str
    budget: float
    allocation: dict[str, float]
    summary: str
    recommendations: list[RecommendationItem]
    ai_powered: bool
    warnings: list[str] = Field(default_factory=list)
