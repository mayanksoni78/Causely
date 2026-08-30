class StripeRegister(BaseModel):
    api_key: str

class Auth0Register(BaseModel):
    domain: str
    client_id: str
    client_secret: str

class GithubActionsRegister(BaseModel):
    repo_url: str
    token: str

@router.post("/stripe")
async def register_stripe(
    payload: StripeRegister,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    from src.connectors.stripe import StripeConnector
    config = {"api_key": payload.api_key}
    connector = StripeConnector(str(uuid.uuid4()), str(user.tenant_id), config)
    health = connector.health_check()
    if not health.healthy:
        raise HTTPException(status_code=400, detail=f"Connection failed: {health.message}")

    new_source = DBSource(
        tenant_id=user.tenant_id,
        type="stripe",
        category="external_services",
        name="Stripe",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected",
        capabilities=connector.list_capabilities()
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

@router.post("/auth0")
async def register_auth0(
    payload: Auth0Register,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    from src.connectors.auth0 import Auth0Connector
    config = {"domain": payload.domain, "client_id": payload.client_id, "client_secret": payload.client_secret}
    connector = Auth0Connector(str(uuid.uuid4()), str(user.tenant_id), config)
    health = connector.health_check()
    if not health.healthy:
        raise HTTPException(status_code=400, detail=f"Connection failed: {health.message}")

    new_source = DBSource(
        tenant_id=user.tenant_id,
        type="auth0",
        category="external_services",
        name="Auth0",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected",
        capabilities=connector.list_capabilities()
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}

@router.post("/github-actions")
async def register_github_actions(
    payload: GithubActionsRegister,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    from src.connectors.github_actions import GitHubActionsConnector
    config = {"repo_url": payload.repo_url, "token": payload.token}
    connector = GitHubActionsConnector(str(uuid.uuid4()), str(user.tenant_id), config)
    health = connector.health_check()
    if not health.healthy:
        raise HTTPException(status_code=400, detail=f"Connection failed: {health.message}")

    new_source = DBSource(
        tenant_id=user.tenant_id,
        type="github_actions",
        category="code",
        name="GitHub Actions",
        config={"encrypted_data": encrypt_dict(config)},
        status="connected",
        capabilities=connector.list_capabilities()
    )
    db.add(new_source)
    db.commit()
    return {"id": str(new_source.id)}
