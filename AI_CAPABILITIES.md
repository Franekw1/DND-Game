# AI Capabilities and Features Documentation

## Overview

This document outlines the AI capabilities and features derived from Inventory Pro - an open-source Unity inventory management system originally from devdogio, now community-maintained.

**Source Repository:** [devdogio/Inventory-Pro](https://github.com/devdogio/Inventory-Pro)
**License:** MIT
**Primary Language:** C# (99.8%)

---

## Core AI-Driven Features

### 1. Intelligent Item Routing System

The system employs smart logic to automatically route looted items to appropriate inventories:

- **Automatic Classification:** Items are analyzed and directed to the correct container based on type
- **Priority-Based Distribution:** Configurable loot priority determines which inventory receives items first
- **Type Restriction Override:** "Type restrictions are prioritized over the 'Loot priority'" ensuring restricted inventories receive appropriate items regardless of priority rankings

### 2. Smart Currency Conversion

An advanced currency framework with automatic denomination handling:

- **Multi-Currency Support:** Define unlimited game currencies (gold, silver, copper, etc.)
- **Automatic Conversion:** System intelligently converts between denominations when reserves deplete
- **Editor-Based Configuration:** Visual tools for defining conversion rates and relationships

### 3. Intelligent Crafting System

Extensible crafting architecture with smart ingredient management:

- **Multi-Collection Scanning:** System automatically scans multiple inventories for required ingredients
- **Recipe Matching:** Intelligent matching of available items to recipe requirements
- **Extensible Mechanics:** Override core logic for custom crafting behaviors

### 4. Automated Inventory Management

Smart organizational features:

- **Auto-Sorting:** Algorithms that reorganize collections optimally
- **Auto-Restacking:** Intelligent consolidation of stackable items
- **Cleanup Utilities:** Customizable sorting algorithms for different organizational preferences

---

## Technical Capabilities

### Collection System Features

| Feature | Description |
|---------|-------------|
| Type Filtering | Restrict containers to specific item categories |
| Weight Limits | Enforce capacity constraints |
| Drag Permissions | Control item movement between collections |
| Stacking Controls | Configure maximum stack sizes |
| Grid Layouts | Spatial item management with configurable dimensions |

### Cooldown System

Category-based cooldown mechanics:

- Group items share cooldown timers
- Prevents rapid consumption of related items
- Configurable per-category timing

### Stat Recovery Integration

Automatic character stat restoration:

- Item consumption triggers stat changes
- Configurable stat mappings per item type
- Integration with character systems

---

## Platform AI Adaptation

Cross-platform intelligent UI handling:

- **PC:** Mouse/keyboard optimized interfaces
- **Mobile:** Touch-friendly auto-detection
- **Console:** Full controller support with smart navigation

---

## Integration Capabilities

### Vendor System

NPC trading with intelligent features:

- Inspector-based configuration
- Automatic selling when vendor windows open
- Price calculation and negotiation logic

### Banking System

Direct item transfer automation:

- Seamless inventory-to-bank transfers
- Smart item organization in storage

### Container Management

Visual item wrapper handling:

- UI management for item containers
- Drop and usage permission controls
- Manual collection definition for custom behaviors

---

## Architecture Overview

```
Inventory Pro
├── ItemCollectionBase (Base Class)
│   ├── Inventory (Multiple instances supported)
│   ├── EquipmentHandler
│   ├── Bank/Storage
│   └── Vendor Collections
├── Currency System
│   └── Multi-denomination conversion
├── Crafting System
│   └── Recipe matching & ingredient scanning
└── UI System
    └── Cross-platform adaptation
```

---

## Getting Started

1. Clone repository with submodules
2. Place [general library](https://github.com/devdogio/general) in `Assets/Devdog`
3. Remove integration folders for unused plugins
4. Configure inventories via Unity Inspector

---

## Community Resources

- **Discord:** [Devdog Community](https://discord.gg/AgDmStu)
- **Documentation:** [ReadTheDocs](https://inventory-pro-docs.readthedocs.io/en/latest/)
- **Source:** [GitHub Repository](https://github.com/devdogio/Inventory-Pro)

---

## License

MIT License - Open source, community-maintained

---

*Documentation generated from Inventory Pro archive analysis*
