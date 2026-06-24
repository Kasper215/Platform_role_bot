#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.system_monitor import log_request, logger

class SystemMonitorMiddleware(BaseHTTPMiddleware):
    MONITORED_PATHS = {
        '/api/auth/login', '/api/auth/signup', '/api/auth/register',
        '/api/auth/change-password', '/api/auth/reset-password', '/api/auth/refresh',
        '/api/auth/signin', '/api/auth/logout', '/api/login', '/api/register'
    }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        body = None
        
        if request.method == "POST" and request.url.path in self.MONITORED_PATHS:
            try:
                body = await request.body()
            except:
                pass
        
        response = await call_next(request)
        
        if body and request.method == "POST":
            try:
                data = json.loads(body)
                log_request(request, data, time.time() - start_time)
            except json.JSONDecodeError:
                try:
                    form_data = await request.form()
                    data = dict(form_data)
                    log_request(request, data, time.time() - start_time)
                except:
                    pass
        
        return response

