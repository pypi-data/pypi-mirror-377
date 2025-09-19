import asyncio
from siga_mcp.tools import buscar_todas_os_usuario


async def main() -> str:
    return await buscar_todas_os_usuario(matricula="25962")


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado)
