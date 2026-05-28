# Tradeoffs

## What We Didn't Build

### 1. Real-Time Data Streaming
**Why not:** Adds infrastructure complexity (WebSockets, Redis). Most uploads are batch operations.
**Alternative:** Simple polling for status checks.

### 2. Advanced Analytics & ML
**Why not:** Requires large, clean datasets. Analytics is a separate product category.
**Alternative:** Export functionality for external analysis tools.

### 3. Complex Rate Structure Support
**Why not:** Rate data not available in CSV exports. Varies wildly by utility provider.
**Alternative:** Store total cost, let users analyze externally.

## Philosophy
> "Perfect is the enemy of good. We'd rather have a solid foundation that works well today."