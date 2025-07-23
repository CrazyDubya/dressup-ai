# DressUp AI - Optimization and Enhancement Recommendations

## Performance Optimizations

### 1. Algorithm Optimizations

#### Current Issues:
- O(n²) complexity in outfit matching algorithms
- Redundant calculations in material property evaluations
- No caching of computed results

#### Recommended Solutions:

```python
# Add caching decorator for expensive calculations
from functools import lru_cache
import redis

class OutfitGenerator:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    @lru_cache(maxsize=1000)
    def calculate_material_suitability(self, material, season, weather):
        """Cache material suitability calculations."""
        # Expensive calculation logic here
        pass
    
    def get_cached_outfit(self, user_hash, context_hash):
        """Retrieve cached outfit recommendations."""
        cache_key = f"outfit:{user_hash}:{context_hash}"
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        return None
```

### 2. Database Optimization

#### Replace CSV with Proper Database:

```python
# Replace CSV operations with SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class OutfitHistory(Base):
    __tablename__ = 'outfit_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), index=True)
    outfit_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    rating = Column(Float)

# Use connection pooling
engine = create_engine(
    'postgresql://user:pass@localhost/dressup_ai',
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

### 3. Async Processing

#### Implement async endpoints:

```python
from fastapi import FastAPI, BackgroundTasks
import asyncio

@app.post("/api/generate/outfit-async")
async def generate_outfit_async(request: OutfitRequest, background_tasks: BackgroundTasks):
    """Generate outfit asynchronously for better performance."""
    task_id = str(uuid.uuid4())
    
    # Store task status
    await redis_client.set(f"task:{task_id}", "processing")
    
    # Start background task
    background_tasks.add_task(process_outfit_generation, task_id, request)
    
    return {"task_id": task_id, "status": "processing"}

async def process_outfit_generation(task_id: str, request: OutfitRequest):
    """Process outfit generation in background."""
    try:
        outfit = await generate_outfit_async_impl(request)
        await redis_client.set(f"task:{task_id}", json.dumps({
            "status": "completed",
            "result": outfit
        }))
    except Exception as e:
        await redis_client.set(f"task:{task_id}", json.dumps({
            "status": "failed",
            "error": str(e)
        }))
```

## Security Enhancements

### 1. Authentication and Authorization

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def create_access_token(self, user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    auth_manager = AuthManager(settings.SECRET_KEY)
    payload = auth_manager.verify_token(credentials.credentials)
    return payload["user_id"]

@app.post("/api/generate/outfit")
async def generate_outfit(
    request: OutfitRequest,
    user_id: str = Depends(get_current_user)
):
    """Protected endpoint requiring authentication."""
    pass
```

### 2. Input Validation and Sanitization

```python
from pydantic import validator, Field
import bleach

class SecureOutfitRequest(BaseModel):
    profile_name: str = Field(..., min_length=1, max_length=100)
    user_profile: Dict
    event_context: Dict
    
    @validator('profile_name')
    def sanitize_profile_name(cls, v):
        # Remove potentially dangerous characters
        sanitized = bleach.clean(v, tags=[], strip=True)
        if not sanitized.replace(' ', '').replace('-', '').replace('_', '').isalnum():
            raise ValueError('Profile name contains invalid characters')
        return sanitized
    
    @validator('user_profile')
    def validate_user_profile(cls, v):
        required_fields = ['height', 'weight']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Missing required field: {field}')
        
        # Validate numeric ranges
        if not 100 <= v.get('height', 0) <= 250:
            raise ValueError('Height must be between 100-250 cm')
        
        return v
```

### 3. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/generate/outfit")
@limiter.limit("10/minute")
async def generate_outfit(request: Request, outfit_request: OutfitRequest):
    """Rate-limited outfit generation endpoint."""
    pass
```

## Code Quality Improvements

### 1. Refactoring Large Classes

#### Break down the monolithic DressMaker class:

```python
# material_selector.py
class MaterialSelector:
    """Handles material selection logic."""
    
    def __init__(self, material_specs: MaterialSpecifications):
        self.material_specs = material_specs
    
    def select_optimal_material(
        self, 
        item_type: str, 
        season: str, 
        weather_conditions: List[str],
        user_preferences: List[str]
    ) -> str:
        """Select the most appropriate material."""
        pass

# style_coordinator.py
class StyleCoordinator:
    """Handles style coordination and matching."""
    
    def coordinate_outfit_colors(self, primary_colors: List[str]) -> Dict[str, str]:
        """Coordinate colors for a complete outfit."""
        pass
    
    def match_formality_levels(self, event_context: EventContext) -> int:
        """Determine appropriate formality level."""
        pass

# outfit_assembler.py
class OutfitAssembler:
    """Assembles complete outfits from components."""
    
    def __init__(self, material_selector: MaterialSelector, style_coordinator: StyleCoordinator):
        self.material_selector = material_selector
        self.style_coordinator = style_coordinator
    
    def assemble_outfit(self, requirements: OutfitRequirements) -> OutfitData:
        """Assemble a complete outfit."""
        materials = self.material_selector.select_optimal_material(...)
        colors = self.style_coordinator.coordinate_outfit_colors(...)
        # Assembly logic
        return OutfitData(...)
```

### 2. Error Handling Standardization

```python
class DressUpAIException(Exception):
    """Base exception for DressUp AI."""
    pass

class ValidationError(DressUpAIException):
    """Raised when input validation fails."""
    pass

class GenerationError(DressUpAIException):
    """Raised when outfit generation fails."""
    pass

class MaterialError(DressUpAIException):
    """Raised when material-related errors occur."""
    pass

# Centralized error handler
@app.exception_handler(DressUpAIException)
async def dressup_exception_handler(request: Request, exc: DressUpAIException):
    logger.error(f"DressUpAI Error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### 3. Configuration Management

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://localhost/dressup_ai"
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # Performance
    cache_ttl_seconds: int = 3600
    max_outfit_generation_time: int = 30
    
    # External APIs
    weather_api_key: str = ""
    image_generation_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Architecture Enhancements

### 1. Microservices Architecture

```python
# user_service/main.py
@app.post("/users/{user_id}/profile")
async def update_user_profile(user_id: str, profile: UserProfile):
    """User profile management service."""
    pass

# outfit_service/main.py
@app.post("/outfits/generate")
async def generate_outfit(request: OutfitRequest):
    """Outfit generation service."""
    pass

# material_service/main.py
@app.get("/materials/{material_id}")
async def get_material_details(material_id: str):
    """Material information service."""
    pass

# recommendation_service/main.py
@app.post("/recommendations/personalized")
async def get_personalized_recommendations(user_id: str):
    """ML-based recommendation service."""
    pass
```

### 2. Event-Driven Architecture

```python
from dataclasses import dataclass
from typing import Dict, Any
import asyncio

@dataclass
class DomainEvent:
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    user_id: str

class EventBus:
    def __init__(self):
        self.handlers = {}
    
    def subscribe(self, event_type: str, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def publish(self, event: DomainEvent):
        handlers = self.handlers.get(event.event_type, [])
        await asyncio.gather(*[handler(event) for handler in handlers])

# Usage
event_bus = EventBus()

# Subscribe to events
event_bus.subscribe("outfit_generated", update_user_preferences)
event_bus.subscribe("outfit_generated", log_generation_metrics)
event_bus.subscribe("outfit_rated", update_recommendation_model)

# Publish events
await event_bus.publish(DomainEvent(
    event_type="outfit_generated",
    data={"outfit_id": "123", "user_feedback": "positive"},
    timestamp=datetime.utcnow(),
    user_id="user123"
))
```

### 3. Monitoring and Observability

```python
from prometheus_client import Counter, Histogram, generate_latest
import structlog

# Metrics
outfit_generation_counter = Counter('outfit_generations_total', 'Total outfit generations')
generation_duration = Histogram('outfit_generation_duration_seconds', 'Outfit generation duration')

# Structured logging
logger = structlog.get_logger()

class OutfitGenerationService:
    @generation_duration.time()
    async def generate_outfit(self, request: OutfitRequest) -> OutfitResponse:
        logger.info("Starting outfit generation", user_id=request.user_id)
        
        try:
            outfit = await self._perform_generation(request)
            outfit_generation_counter.inc()
            logger.info("Outfit generation completed", 
                       user_id=request.user_id, 
                       outfit_id=outfit.id)
            return outfit
        except Exception as e:
            logger.error("Outfit generation failed", 
                        user_id=request.user_id, 
                        error=str(e))
            raise

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")
```

## Testing Improvements

### 1. Comprehensive Test Strategy

```python
import pytest
from unittest.mock import Mock, patch
from httpx import AsyncClient

class TestOutfitGeneration:
    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_generate_outfit_success(self, client):
        """Test successful outfit generation."""
        request_data = {
            "profile_name": "casual_user",
            "user_profile": {"height": 170, "weight": 65},
            "event_context": {"formality": 3, "season": "summer"}
        }
        
        response = await client.post("/api/generate/outfit", json=request_data)
        assert response.status_code == 200
        
        outfit = response.json()
        assert "design" in outfit
        assert "materials" in outfit
    
    @pytest.mark.asyncio
    async def test_generate_outfit_invalid_input(self, client):
        """Test outfit generation with invalid input."""
        request_data = {"invalid": "data"}
        
        response = await client.post("/api/generate/outfit", json=request_data)
        assert response.status_code == 422

# Performance tests
class TestPerformance:
    @pytest.mark.performance
    async def test_outfit_generation_performance(self):
        """Test outfit generation performance."""
        start_time = time.time()
        
        # Generate 100 outfits
        tasks = []
        for _ in range(100):
            task = generate_outfit(sample_request)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        assert duration < 10.0  # Should complete in under 10 seconds
        
    @pytest.mark.load
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        async with AsyncClient(app=app) as client:
            tasks = []
            for _ in range(50):
                task = client.post("/api/generate/outfit", json=sample_request)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # All requests should succeed
            assert all(r.status_code == 200 for r in responses)
```

### 2. Integration Testing

```python
@pytest.mark.integration
class TestIntegration:
    async def test_end_to_end_outfit_generation(self):
        """Test complete outfit generation workflow."""
        # 1. Create user profile
        user_response = await client.post("/api/users", json=user_data)
        user_id = user_response.json()["user_id"]
        
        # 2. Generate outfit
        outfit_response = await client.post("/api/generate/outfit", json={
            "user_id": user_id,
            **outfit_request
        })
        outfit = outfit_response.json()
        
        # 3. Verify outfit was saved
        history_response = await client.get(f"/api/users/{user_id}/outfits")
        assert len(history_response.json()) == 1
        
        # 4. Rate outfit
        rating_response = await client.post(f"/api/outfits/{outfit['id']}/rate", json={
            "rating": 5,
            "feedback": "Great outfit!"
        })
        assert rating_response.status_code == 200
```

These enhancements will significantly improve the performance, security, maintainability, and scalability of the DressUp AI system. The recommendations should be implemented incrementally, starting with the highest-priority security and performance fixes.