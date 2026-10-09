"""Main FastAPI application for Clean Loop backend."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 {settings.app_name} v{settings.app_version} starting up...")

    yield

    # Shutdown
    print(f"👋 {settings.app_name} shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# Clean Loop - AI-Assisted Smart Waste Management Platform

A comprehensive backend for managing waste disposal, complaints, and municipal analytics.

## Features

- **Authentication**: JWT-based auth with role-based access control
- **Waste Classification**: AI-powered waste categorization
- **Facilities Management**: Location-based facility discovery
- **Complaint System**: Full complaint lifecycle with status history
- **Offline Support**: Sync complaints created offline
- **Analytics Dashboard**: Municipal-level insights and hotspots

## User Roles

- **citizen**: Submit complaints, view facilities, track issues
- **municipal_staff**: Update complaint status, view analytics
- **admin**: Full system access

## Getting Started

1. Register at `/api/v1/auth/register`
2. Login at `/api/v1/auth/login` to get JWT token
3. Use token in `Authorization: Bearer <token>` header
    """,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Returns basic API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns 200 OK if service is healthy.
    """
    return {"status": "healthy", "environment": settings.environment}
