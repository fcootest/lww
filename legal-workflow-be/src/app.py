"""FastAPI application initialization."""

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.common.response import send_success
from src.auth.dependencies import get_current_user, require_roles


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Startup: init DB + seed data ---
    @app.on_event("startup")
    async def startup():
        from src.config.database import init_db, table_has_data
        init_db()

        # Only seed if tables are empty (data persists in SQLite)
        if not table_has_data("tst"):
            from src.seeds.seed_tst import seed_all as seed_tst
            seed_tst()
            from src.seeds.seed_tnt import seed_all as seed_tnt
            seed_tnt()
            from src.seeds.seed_emp import seed_all as seed_emp
            seed_emp()
            from src.seeds.seed_tst_trt import seed_all as seed_tst_trt
            seed_tst_trt()
            from src.seeds.seed_tri import seed_all as seed_tri
            seed_tri()
            from src.seeds.seed_lf210_config import seed_all as seed_lf210_config
            seed_lf210_config()
            from src.seeds.seed_lf220_config import seed_all as seed_lf220_config
            seed_lf220_config()
            from src.seeds.seed_lf230_config import seed_all as seed_lf230_config
            seed_lf230_config()
            from src.seeds.seed_lf240_config import seed_all as seed_lf240_config
            seed_lf240_config()
            print("[STARTUP] Seed data loaded into SQLite")
        else:
            print("[STARTUP] SQLite database already has data, skipping seed")

    # Health check (public)
    @app.get("/api/health")
    async def health_check():
        return send_success(
            data={"version": settings.APP_VERSION},
            message="OK",
        )

    # --- Test routes (for auth testing, will be removed later) ---

    @app.get("/api/test/protected")
    async def test_protected(request: Request, user: dict = Depends(get_current_user)):
        """Test route: requires valid JWT."""
        return send_success(data=user)

    @app.get("/api/test/admin-only")
    async def test_admin_only(request: Request, user: dict = Depends(require_roles(["ADMIN"]))):
        """Test route: ADMIN role only."""
        return send_success(data=user)

    @app.get("/api/test/manager-or-admin")
    async def test_manager_or_admin(
        request: Request,
        user: dict = Depends(require_roles(["ADMIN", "LEGAL_MANAGER"])),
    ):
        """Test route: ADMIN or LEGAL_MANAGER."""
        return send_success(data=user)

    # --- Register routers ---
    from src.modules.tst.router import router as tst_router
    from src.modules.tnt.router import router as tnt_router
    from src.modules.tdt.router import router as tdt_router
    from src.modules.tdtp.router import router as tdtp_router
    from src.modules.trt.router import router as trt_router
    from src.modules.filters.router import router as filters_router
    from src.modules.emp.router import router as emp_router
    from src.modules.tsi.router import router as tsi_router
    from src.modules.tsev.router import router as tsev_router
    from src.modules.tri.router import router as tri_router
    from src.modules.tdi.router import router as tdi_router
    from src.modules.tsi.my_tasks_router import router as my_tasks_router
    from src.modules.dashboard.router import router as dashboard_router
    from src.modules.reports.router import router as reports_router
    from src.modules.ai_review.router import router as ai_review_router
    from src.modules.sec.router import router as sec_router

    app.include_router(tst_router)
    app.include_router(tnt_router)
    app.include_router(tdt_router)
    app.include_router(tdtp_router)
    app.include_router(trt_router)
    app.include_router(filters_router)
    app.include_router(emp_router)
    app.include_router(tsi_router)
    app.include_router(tsev_router)
    app.include_router(tri_router)
    app.include_router(tdi_router)
    app.include_router(my_tasks_router)
    app.include_router(dashboard_router)
    app.include_router(reports_router)
    app.include_router(ai_review_router)
    app.include_router(sec_router)

    return app


app = create_app()
