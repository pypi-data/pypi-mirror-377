import base64
import logging
from collections import deque

logger = logging.getLogger(__name__)

class MemoryBank:
    def __init__(self, start, end, data : bytearray | str = None, fillValue = 0):
        self.start = start
        self.end = end
        self.prevPublished = None

        if data == None:
            self.data = bytearray([fillValue] * (end - start))
        elif type(data) == str:
            self.data : bytearray = base64.b64decode(data)
        elif type(data) == bytes:
            self.data : bytearray = bytearray(data)
        else:
            self.data : bytearray = data

        if len(self.data) < end - start:
            #fill the rest of the data with 0s
            addLen = (end - start) - len(self.data)
            addon = bytearray([fillValue] * addLen)
            self.data += addon
            logger.warning(f"Data for bank {start} to {end} was padded with 0s")
        if len(self.data) > end - start:
            #truncate the data
            self.data = self.data[:end - start]
            logger.warning(f"Data for bank {start} to {end} was truncated")



    def extend(self, newStart, newEnd, fillValue = 0):
       
        if newStart < self.start:
           #pad the data with 0s
           preLen = self.start - newStart
           preData = bytearray([fillValue] * preLen)
           self.data = preData + self.data
           self.start = newStart
        
        if newEnd > self.end:
            #pad the data with 0s
            postLen = newEnd - self.end
            postData = bytearray([fillValue] * postLen)
            self.data = self.data + postData
            self.end = newEnd

    def write(self, address, data: bytearray):
        write_start = address
        write_end = address + len(data)

        overlap_start = max(write_start, self.start)
        overlap_end = min(write_end, self.end)

        if overlap_start > overlap_end:
            return
        
        # Calculate indices relative to self.data and data
        bytearray_start_index = overlap_start - self.start
        bytearray_end_index = overlap_end - self.start

        data_start_index = overlap_start - write_start
        data_end_index = overlap_end - write_start
        self.data[bytearray_start_index:bytearray_end_index] = data[data_start_index:data_end_index]

        
        

    def read(self, address, length):
        index = 0
        data = bytearray(length)
        if address >= self.start and address <= self.end:
            cursor = address - self.start

            while(cursor <= self.end and index < length):

                data[index] = self.data[cursor]
                cursor += 1
                index += 1

            return data
        
        return data


class MemoryFifo(MemoryBank):
    def __init__(self, start, end = None, size = None):

        if end == None:
            end = start

        super().__init__(start, end)

        self.buffer = deque( maxlen=size) 


    def extend(self, newStart, newEnd, fillValue=0):
        pass

    def write(self, address, data: bytearray):

        for byte in data:
            self.buffer.append(byte)
        
    def read(self, address, length):
        
        if len(self.buffer) <= length:
            length = len(self.buffer)
        
        return bytearray(self.buffer[:length])


class EmulatedMemory:
    def __init__(self, regBanks : list[MemoryBank] = [], autoMutation = True, fillValue = 0):
        """
            regBanks: list of RegisterBank objects to start with
            autoMutate: If true, will generate and modify banks as needed when performing operations
            fillValue: The value to fill new banks/segments with
        """

        self.regBanks = regBanks
        self.cursor = 0
        self.autoMutation = autoMutation
        self.fillValue = fillValue


    def autoMutate(self, address, size):
        """
            Check to see if any banks need to be extended or created to write data
            if a bank extends to another bank, it will be merged
        """

        touchedBanks : list[MemoryBank] = []

        op_start = address
        op_end = address + size

        #Get a list of banks that overlap with the range
        for bank in self.regBanks:
            if bank.start <= op_start and bank.end >= op_end:
                touchedBanks.append(bank)

        #If no banks were touched, create a new bank
        if len(touchedBanks) == 0:
            newBank = MemoryBank(op_start, op_end)
            self.regBanks.append(newBank)
            return
        elif len(touchedBanks) == 1:
        #If only one bank was touched, extend it if needed and return
            touchedBanks[0].extend(op_start, op_end, fillValue = self.fillValue)
        elif len(touchedBanks) > 1:
            
            #sort the banks by start address
            touchedBanks.sort(key=lambda x: x.start)

            #Create a new bank that spans all the touched banks and any extra space outside of them
            newStart = min(touchedBanks[0].start, op_start)
            newEnd = max(touchedBanks[-1].end, op_end)
            newBank = MemoryBank(newStart, newEnd,[], self.fillValue)

            #copy the data from the touched banks into the new bank
            for bank in touchedBanks:
                offset = bank.start - newStart
                newBank.data[offset:offset + len(bank.data)] = bank.data
                #remove the old bank
                self.regBanks.remove(bank)
            
            #add the new bank
            self.regBanks.append(newBank)

        
        
    def write(self, address, data: bytearray):

        if self.autoMutation:
            self.autoMutate(address, len(data))

        index = 0
        for bank in self.regBanks:
            bank.write(address, data) #The bank will handle the data bounds and writing

        self.cursor = address + len(data) + 1
            
    def read(self, address, length):
        index = 0
        data = bytearray([self.fillValue] * length)


        for bank in self.regBanks:

            block = bank.read(address, length)
            offset = bank.start - address
            if block:
                data[offset:offset + len(block)] = block
                index += len(block)
        
        return data
    
    def hexDump(self, start = None, end = None, width = 16):
        """
            Print a hex dump of the memory aligned to the width (padding before and after with --)

            ff000:          03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f  0123456789abcdef
            ff010: 10 11 12 13 -- -- -- -- -- -- -- 1b 1c 1d 1e 1f  0123456789abcdef
            ff020: 20 21 22 23 24 25 26 27 28 29 2a 2b              0123456789abcdef  
            -----         
            ffff0: 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11  0123456789abcdef
        """
        
        lines = []

        self.regBanks.sort(key=lambda x: x.start)

        if start == None:
            start = self.regBanks[0].start
        
        if end == None:
            end = self.regBanks[-1].end

        addrSize = len(hex(end)) - 2
        if addrSize < 4:
            addrSize = 4

        idx = 0
        lastEnd = 0

        for bank in self.regBanks:

            frontPad = bank.start % width
            backPad = width - (bank.end % width)

            if idx > 0 and bank.start > (lastEnd + 1):
                lines.append("-" * addrSize)

            strAddr = f"{bank.start:0{addrSize}x}"
            strHex = " " * (frontPad * 3) + " ".join([f"{byte:02x}" for byte in bank.data])
            strAscii = "".join([chr(byte) if byte >= 32 and byte <= 126 else "." for byte in bank.data])

            lines.append(f"{strAddr}: {strHex}  {strAscii}")

            for i in range(bank.start + frontPad, bank.end, width):
                chunk = bank.data[i - bank.start:i - bank.start + width]
                strAddr = f"{i:0{addrSize}x}"
                strHex = " ".join([f"{byte:02x}" for byte in chunk])
                strAscii = "".join([chr(byte) if byte >= 32 and byte <= 126 else "." for byte in chunk])
                lines.append(f"{strAddr}: {strHex}  {strAscii}")

            idx+= 1
            lastEnd = bank.end 
        
        return "\n".join(lines)



              



            



        
    

