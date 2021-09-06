def recogniseGesture(landmarkPoints: str) -> str:
    splitLMs = landmarkPoints.split('landmark')[1:]
    formattedLMs = [dict(s.strip()) for s in splitLMs]
    pass