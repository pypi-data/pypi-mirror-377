#!/usr/bin/env python3
"""
MCP Minder Client Usage Examples

This script demonstrates how to use the MCP Minder client library
to interact with remote MCP Minder API services.
"""

import asyncio
from minder.client import McpMinder, McpMinderError


async def async_example():
    """Async usage example."""
    print("=== Async Usage Example ===")
    
    # Create client instance
    minder = McpMinder.get_service(
        url="http://localhost:8000", 
        servername="my_mcp_server"
    )
    
    try:
        # Check server health
        if not await minder.health_check():
            print("❌ MCP Minder server is not healthy")
            return
        
        print("✅ MCP Minder server is healthy")
        
        # Get service information
        info = await minder.get_info()
        print(f"📋 Service Info: {info}")
        
        # Start service on port 8080
        result = await minder.start(port=8080)
        print(f"🚀 Service started: {result}")
        
        # Check status
        status = await minder.get_status()
        print(f"📊 Service status: {status}")
        
        # Get logs
        logs = await minder.get_logs(lines=10)
        print(f"📝 Recent logs:\n{logs}")
        
        # Restart service
        result = await minder.restart(port=8081)
        print(f"🔄 Service restarted: {result}")
        
        # Stop service
        result = await minder.stop()
        print(f"🛑 Service stopped: {result}")
        
    except McpMinderError as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        await minder._close()


def sync_example():
    """Synchronous usage example."""
    print("\n=== Sync Usage Example ===")
    
    # Create client instance
    minder = McpMinder.get_service(
        url="http://localhost:8000", 
        servername="my_mcp_server"
    )
    
    try:
        # Check server health
        if not minder.health_check_sync():
            print("❌ MCP Minder server is not healthy")
            return
        
        print("✅ MCP Minder server is healthy")
        
        # Get service information
        info = minder.get_info_sync()
        print(f"📋 Service Info: {info}")
        
        # Start service on port 8080
        result = minder.start_sync(port=8080)
        print(f"🚀 Service started: {result}")
        
        # Check status
        status = minder.get_status_sync()
        print(f"📊 Service status: {status}")
        
        # Get logs
        logs = minder.get_logs_sync(lines=10)
        print(f"📝 Recent logs:\n{logs}")
        
        # Stop service
        result = minder.stop_sync()
        print(f"🛑 Service stopped: {result}")
        
    except McpMinderError as e:
        print(f"❌ Error: {e}")


def context_manager_example():
    """Context manager usage example."""
    print("\n=== Context Manager Example ===")
    
    # Using context manager (sync)
    with McpMinder.get_service("http://localhost:8000", "my_mcp_server") as minder:
        try:
            info = minder.get_info_sync()
            print(f"📋 Service Info: {info}")
            
            result = minder.start_sync(port=8080)
            print(f"🚀 Service started: {result}")
            
        except McpMinderError as e:
            print(f"❌ Error: {e}")


async def async_context_manager_example():
    """Async context manager usage example."""
    print("\n=== Async Context Manager Example ===")
    
    # Using async context manager
    async with McpMinder.get_service("http://localhost:8000", "my_mcp_server") as minder:
        try:
            info = await minder.get_info()
            print(f"📋 Service Info: {info}")
            
            result = await minder.start(port=8080)
            print(f"🚀 Service started: {result}")
            
        except McpMinderError as e:
            print(f"❌ Error: {e}")


def list_services_example():
    """List all services example."""
    print("\n=== List All Services Example ===")
    
    minder = McpMinder.get_service("http://localhost:8000", "dummy")
    
    try:
        services = minder.list_all_services_sync()
        print(f"📋 Found {len(services)} services:")
        
        for service in services:
            print(f"  - {service.name}: {service.status} (port: {service.port})")
            
    except McpMinderError as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples."""
    print("MCP Minder Client Usage Examples")
    print("=" * 50)
    
    # Run sync examples
    sync_example()
    context_manager_example()
    list_services_example()
    
    # Run async examples
    asyncio.run(async_example())
    asyncio.run(async_context_manager_example())


if __name__ == "__main__":
    main()
