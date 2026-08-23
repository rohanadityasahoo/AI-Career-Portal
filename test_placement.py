from ai_modules.placement_predictor import predict_placement

result, score = predict_placement(
    75,
    70,
    80
)

print(result)
print(score)