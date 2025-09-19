from termcolor import colored  

def hexdump(data: bytes, width: int = 16, showAscii= True, colors=['green','yellow','cyan']) -> str:
    """
    Format bytes into a hex dump string.

    Args:
        data (bytes): The byte data to format.
        width (int): Number of bytes per line in the hex dump.
        showAscii (bool): Whether to show ASCII representation.
    Returns:
        str: Formatted hex dump string.
    """
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]

        #hex_part = ' '.join(f'{byte:02x}' for byte in chunk)
        hex_part = colored(' '.join(f'{byte:02x}' for byte in chunk), colors[1])

        ascii_part = colored(''.join((chr(byte) if 32 <= byte < 127 else '.') for byte in chunk), colors[2])
        adddress = colored(f"{i:04x}", colors[0])
        if showAscii:
            lines.append(f"    {adddress}: {hex_part:<{width * 3}} {ascii_part}")
        else:
            lines.append(f"    {adddress}: {hex_part:<{width * 3}}")
    return '\n'.join(lines)
