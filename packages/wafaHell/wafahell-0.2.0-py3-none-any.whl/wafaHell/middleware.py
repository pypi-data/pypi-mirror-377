import re
from flask import request as req, abort
from urllib.parse import unquote
from model import Blocked, get_session
from logger import Logger
from utils import is_block_expired
from rateLimiter import RateLimiter
from sqlalchemy.exc import OperationalError

# Inicializa o RateLimiter
limiter = RateLimiter(limit=100, window=60)

class WafaHell:
    def __init__(self, app=None, block_code=403, log_func=None, monitor_mode=False, block_ip=False, rate_limit=False):
        self.app = app
        self.block_code = block_code
        self.log = log_func or Logger()
        self.monitor_mode = monitor_mode
        self.block_ip = block_ip
        self.rate_limit = rate_limit

        self.rules = [
            r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDROP\b)",  
            r"' OR '1'='1",                                
            r"<script.*?>.*?</script>",                    
            r"javascript:",                                
        ]

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Configura a sessão para cada requisição
        @app.before_request
        def create_session():
            try:
                req.session = get_session()  # Cria uma nova sessão usando get_session
            except Exception as e:
                self.log.error(f"Erro ao criar sessão para requisição: {e}")
                abort(self.block_code)  # Retorna erro 500 se não conseguir criar a sessão

        # Fecha a sessão após cada requisição
        @app.teardown_request
        def close_session(exc=None):
            if hasattr(req, 'session'):
                try:
                    req.session.close()  # Fecha a sessão para liberar a conexão
                except Exception as e:
                    self.log.error(f"Erro ao fechar sessão: {e}")

        @app.before_request
        def waf_check():
            self.verify_client_blocked(req)
            self.verify_rate_limit(req)
            is_malicious, attack_local, payload = self.is_malicious(req)
            
            if not is_malicious:
                return
            
            if not self.monitor_mode:
                self.log.warning(self.parse_req(req, payload,attack_local))
                self.block_ip_address(req.remote_addr, req.headers.get("User-Agent", "unknown"))
            else:
                self.log.info(self.parse_req(req, payload, attack_local))

    def detect_attack(self, data: str) -> bool:
        for pattern in self.rules:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False

    def is_malicious(self, req) -> tuple[bool, str | None, str | None]:
        
        if self.detect_attack(req.base_url):
            return True, "URL", req.base_url

        for key, value in req.args.items():
            if self.detect_attack(value):
                return True, f"QUERY '{key}'", value

        for key, value in req.headers.items():
            if self.detect_attack(value):
                return True, f"HEADER '{key}'", value

        if req.data:
            body_content = req.data.decode(errors="ignore")
            if self.detect_attack(body_content):
                return True, "BODY", body_content
            
        if req.is_json:
            json_data = req.get_json(silent=True)
            if json_data:
                import json
                json_str = json.dumps(json_data)
                if self.detect_attack(json_str):
                    return True, "JSON BODY", json_str

        return False, None, None

    def verify_client_blocked(self, req) -> None:
        session = req.session
        try:
            client_blocked = session.query(Blocked).filter_by(
                ip=req.remote_addr, user_agent=req.headers.get("User-Agent")
            ).first()
            if client_blocked:
                if is_block_expired(client_blocked.blocked_at):
                    session.delete(client_blocked)
                    session.commit()
                    self.log.info(f"[UNBLOCKED] IP {req.remote_addr} desbloqueado apos expiracao do bloqueio.")
                else:
                    abort(self.block_code)
        except OperationalError as e:
            session.rollback()
            abort(self.block_code)
            

    def block_ip_address(self, ip, user_agent=None):
        if self.block_ip:
            try:
                session = req.session
                blocked_client = Blocked(ip=ip, user_agent=user_agent)
                session.add(blocked_client)
                session.commit()
                self.log.warning(f"[BLOCKED] IP: {ip}, User-Agent: {user_agent}")
            except OperationalError as e:
                self.log.error(f"Erro de banco de dados ao bloquear IP {ip}: {e}")
                session.rollback()
                abort(self.block_code)
            except Exception as e:
                self.log.error(f"Erro ao bloquear IP {ip}: {e}")
                session.rollback()

    def verify_rate_limit(self, req) -> None:
        if self.rate_limit:
            ip = req.remote_addr
            ua = req.headers.get("User-Agent", "unknown")
            if limiter.is_rate_limited(ip, ua):
                self.log.warning(f"[RATE LIMIT] IP: {ip}, User-Agent: {ua} excedeu o limite de requisições.")
                if self.block_ip:
                    self.block_ip_address(ip, ua)
                abort(self.block_code)

    def parse_req(self, req, payload, attack_local=None) -> str:
        ip = req.remote_addr
        user_agent = req.headers.get("User-Agent", "unknown")
        path = req.path
        method = req.method
        attack_local = attack_local or "unknown"
        msg = f"""[ATTACK] IP: {ip}, User-Agent: {user_agent}, Path: {path}, Method: {method}, Payload: {unquote(payload)}, attack_local: {attack_local}"""
        return msg