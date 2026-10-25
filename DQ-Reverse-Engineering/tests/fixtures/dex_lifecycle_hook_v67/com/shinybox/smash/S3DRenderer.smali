.class public Lcom/shinybox/smash/S3DRenderer;
.super Ljava/lang/Object;

.field public bAllowInit:Z
.field public bInitialized:Z

.method public engineShutdown()V
    .registers 1
    return-void
.end method

.method public engineInitialize()Z
    .registers 1
    const/4 v0, 0x1
    return v0
.end method

.method public engineRunOneFrame()Z
    .registers 1
    const/4 v0, 0x1
    return v0
.end method

.method public onDrawFrame(Ljavax/microedition/khronos/opengles/GL10;)V
    .registers 7
    iget-boolean v0, p0, Lcom/shinybox/smash/S3DRenderer;->bAllowInit:Z
    const/4 v1, 0x1
    if-eqz v0, :skip_init
    iget-boolean v0, p0, Lcom/shinybox/smash/S3DRenderer;->bInitialized:Z
    if-nez v0, :skip_init
    invoke-virtual {p0}, Lcom/shinybox/smash/S3DRenderer;->engineShutdown()V
    invoke-virtual {p0}, Lcom/shinybox/smash/S3DRenderer;->engineInitialize()Z
    iput-boolean v1, p0, Lcom/shinybox/smash/S3DRenderer;->bInitialized:Z
    :skip_init
    iget-boolean v0, p0, Lcom/shinybox/smash/S3DRenderer;->bInitialized:Z
    if-eqz v0, :done
    invoke-virtual {p0}, Lcom/shinybox/smash/S3DRenderer;->engineRunOneFrame()Z
    move-result v0
    :done
    return-void
.end method

.method public onShutdown()V
    .registers 1
    invoke-virtual {p0}, Lcom/shinybox/smash/S3DRenderer;->engineShutdown()V
    return-void
.end method
