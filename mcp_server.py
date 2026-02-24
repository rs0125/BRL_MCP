import os
import socket
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

load_dotenv()

mcp = FastMCP("BRL-CAD-Structured-Agent")

BRLCAD_HOST = os.getenv("BRLCAD_HOST", "127.0.0.1")
BRLCAD_PORT = int(os.getenv("BRLCAD_PORT", "5555"))

def send_to_brlcad(cmd: str) -> str:
    """Helper function to talk to the Tcl socket."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        s.connect((BRLCAD_HOST, BRLCAD_PORT))
        s.sendall(f"{cmd}\n".encode('utf-8'))
        return s.recv(4096).decode('utf-8').strip()

# 1. We force the LLM to give us explicit floats and strings, not raw commands
@mcp.tool()
def create_sphere(
    name: str = Field(..., description="Name of the sphere, e.g., 'ball.s'"),
    x: float = Field(..., description="X coordinate of the center"),
    y: float = Field(..., description="Y coordinate of the center"),
    z: float = Field(..., description="Z coordinate of the center"),
    radius: float = Field(..., description="Radius of the sphere")
) -> str:
    """Creates a perfect mathematical sphere in BRL-CAD."""
    
    # Python handles the ugly BRL-CAD syntax so the LLM doesn't have to
    mged_command = f"in {name} sph {x} {y} {z} {radius}"
    
    result = send_to_brlcad(mged_command)
    
    # Automatically draw it so the user sees it
    send_to_brlcad(f"draw {name}")
    send_to_brlcad("autoview")
    
    return f"Created sphere {name} at ({x}, {y}, {z}) with radius {radius}. Output: {result}"

@mcp.tool()
def boolean_combination(
    output_name: str = Field(..., description="Name of the new combined object, e.g., 'donut.c'"),
    base_object: str = Field(..., description="The main object to start with"),
    operator: str = Field(..., description="Must be 'u' (union), '-' (subtract), or '+' (intersect)"),
    target_object: str = Field(..., description="The object being added, subtracted, or intersected")
) -> str:
    """Performs Constructive Solid Geometry (CSG) boolean math."""
    
    if operator not in ['u', '-', '+']:
        return "Error: Operator must be 'u', '-', or '+'."
        
    mged_command = f"comb {output_name} {operator} {base_object} {operator} {target_object}"
    result = send_to_brlcad(mged_command)
    send_to_brlcad(f"draw {output_name}")
    
    return f"Performed CSG: {output_name} = {base_object} {operator} {target_object}. Output: {result}"

if __name__ == "__main__":
    mcp.run()
