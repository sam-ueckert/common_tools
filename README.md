# Introduction 
This is a collection of reused code tools for the InfBIDshbrds projects. Initially this will include an async producer/consumer class and an import of settings from settings.yml

server-hardware shows only ~35 Superdome flex partitions
apis with data:
 - facilities/racks
 - servers/server-hardware
 - servers/server-hardware-types

for server-hardware, we replace all URI with data from URI
server-hardware:
- "model": "HPE Superdome Flex nPartition"
- "processorType": "Intel(R) Xeon(R) Platinum 8280L Processor"
- "romVersion": "3.55.8"
- "serialNumber": "CZ214408QL"
- "serverFirmwareInventoryUri": "/rest/server-hardware/84dac239-a448-5a59-b5dc-91c91e59bc9f/firmware"
- "supportDataCollectionsUri": "/rest/support/data-collections?deviceID=84dac239-a448-5a59-b5dc-91c91e59bc9f&category=server-hardware"
- "supportState": "NotSupported"
- "uri": "/rest/server-hardware/84dac239-a448-5a59-b5dc-91c91e59bc9f"
"subResources": {
                "LocalStorageV2": {
                    "uri": "/rest/server-hardware/84dac239-a448-5a59-b5dc-91c91e59bc9f/localStorageV2",
                },
                "Devices": {
                    "uri": "/rest/server-hardware/84dac239-a448-5a59-b5dc-91c91e59bc9f/devices",
                },
                "MemoryList": {
                    "uri": "/rest/server-hardware/84dac239-a448-5a59-b5dc-91c91e59bc9f/memoryList",
                },
                "Memory": {
                    "uri": "/rest/server-hardware/84dac239-a448-5a59-b5dc-91c91e59bc9f/memory",
                },
                "AdvancedMemoryProtection": {
                    "uri": "/rest/server-hardware/84dac239-a448-5a59-b5dc-91c91e59bc9f/advancedMemoryProtection",
                }
            }

