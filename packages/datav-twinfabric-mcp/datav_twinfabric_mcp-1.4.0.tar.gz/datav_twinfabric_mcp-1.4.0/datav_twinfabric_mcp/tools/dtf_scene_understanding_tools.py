import logging
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP, Context
import os
from http import HTTPStatus

# Get logger
logger = logging.getLogger("TwinFabricMCP")

def register_scene_understanding_tools(mcp: FastMCP):
    """Register TwinFabric Studio tools with the MCP server."""

    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    segment_service_url = os.getenv("SEGMENT_SERVICE_URL")
    segment_service_token = os.getenv("SEGMENT_SERVICE_TOKEN")
    scene_xml_path = os.getenv("SCENE_XML_PATH")
    
    @mcp.tool()
    def identify_object_in_current_screen(
        user_input: str
    ) -> Dict[str, Any]:
        """Based on user's input, identify the object he is concerned about in the current screen."""

        if dashscope_api_key == "" or segment_service_url == "" or segment_service_token == "":
            logger.error("Environment variables not set: DASHSCOPE_API_KEY / SEGMENT_SERVICE_URL / SEGMENT_SERVICE_TOKEN")
            return {"success": False, "message": "Environment variables not set: DASHSCOPE_API_KEY / SEGMENT_SERVICE_URL / SEGMENT_SERVICE_TOKEN"}

        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("identify_object_in_current_screen", {"user_input":user_input, "dashscope_api_key":dashscope_api_key, "segment_service_url":segment_service_url, "segment_service_token":segment_service_token})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"Blueprint creation response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error creating blueprint: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
    @mcp.tool()
    def retrieve_object_with_scene_knowledge(
        user_input: str
    ) -> Dict[str, Any]:
        """Based on user's input, retrieve the object he is concerned about from scene knowledge base."""

        if dashscope_api_key == "" or scene_xml_path == "":
            logger.error("Environment variables not set: DASHSCOPE_API_KEY / SCENE_XML_PATH")
            return {"success": False, "message": "Environment variables not set: DASHSCOPE_API_KEY / SCENE_XML_PATH"}

        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("retrieve_object_with_scene_xml", {"user_input":user_input, "dashscope_api_key":dashscope_api_key, 
            "xml_file_path":scene_xml_path})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"Blueprint creation response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error creating blueprint: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    logger.info("Scene understanding tools registered successfully") 