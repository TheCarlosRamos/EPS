def aggregate(results: dict):
    aggregated = []
    for source, data in results.items():
        for item in data:
            item['source'] = source
            aggregated.append(item)
    return aggregated
