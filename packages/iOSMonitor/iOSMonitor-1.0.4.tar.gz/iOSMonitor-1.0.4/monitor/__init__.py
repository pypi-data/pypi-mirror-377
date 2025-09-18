def run():
    """运行 iOS 性能监控工具的入口点"""
    import asyncio
    from .monitor_sysmon import main
    asyncio.run(main())