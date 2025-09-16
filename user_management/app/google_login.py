# from fastapi import FastAPI, Request, APIRouter
# from fastapi.responses import RedirectResponse, JSONResponse
# from authlib.integrations.starlette_client import OAuth
# import os
# from starlette.middleware.sessions import SessionMiddleware

# router =APIRouter()
# router.add_middleware(SessionMiddleware, secret_key="your_random_secret")

# # Configure OAuth manually (without server_metadata_url)
# oauth = OAuth()
# oauth.register(
#     name="google",
#     client_id=os.getenv("GOOGLE_CLIENT_ID"),
#     client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
#     access_token_url="https://oauth2.googleapis.com/token",         # token endpoint
#     authorize_url="https://accounts.google.com/o/oauth2/v2/auth",  # authorization endpoint
#     api_base_url="https://openidconnect.googleapis.com/v1/",       # base API
#     userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",  # userinfo endpoint
#     client_kwargs={
#         "scope": "openid email profile"
#     }
# )

# @router.get("/login")
# async def login(request: Request):
#     redirect_uri = request.url_for("auth")
#     return await oauth.google.authorize_redirect(request, redirect_uri)

# @router.get("/auth")
# async def auth(request: Request):
#     token = await oauth.google.authorize_access_token(request)
#     user_info = await oauth.google.userinfo(token=token)  # fetch user info manually
#     return JSONResponse(content=user_info)
