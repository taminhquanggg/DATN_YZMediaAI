import insightface

fa = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
fa.prepare(ctx_id=0, det_size=(640, 640))
