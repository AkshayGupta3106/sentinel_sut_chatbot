# Gradient Descent Variants

Batch Gradient Descent computes the gradient of the loss function using the entire training set before each parameter update. It gives a stable, accurate direction of descent but is slow and memory-intensive on large datasets, since one update requires a full pass over all data.

Stochastic Gradient Descent (SGD) updates parameters using the gradient computed from a single training example at a time. This makes updates fast and lets the model start learning immediately, but the path to the minimum is noisy and can oscillate, sometimes helping escape shallow local minima.

Mini-batch Gradient Descent is the practical middle ground used in almost all deep learning: it computes gradients over small batches (typically 32-256 examples), balancing the stability of batch GD with the speed of SGD, and it maps efficiently onto GPU parallelism.

Momentum-based optimizers (SGD with Momentum, Nesterov Accelerated Gradient) accumulate a velocity vector from past gradients to smooth out updates and accelerate convergence in consistent directions, reducing oscillation in ravines of the loss surface.

Adaptive optimizers like Adagrad, RMSprop, and Adam adjust the learning rate per-parameter based on historical gradient magnitudes. Adam, which combines momentum with per-parameter adaptive learning rates, is the most commonly used default optimizer in modern deep learning due to its fast convergence and relative insensitivity to hyperparameter choices.

A common interview question: "Why might Adam generalize worse than SGD with momentum on some tasks?" Answer: Adam's aggressive per-parameter adaptivity can converge to sharper minima that generalize less well; some practitioners use SGD with a well-tuned learning rate schedule for final fine-tuning after Adam gets close.
