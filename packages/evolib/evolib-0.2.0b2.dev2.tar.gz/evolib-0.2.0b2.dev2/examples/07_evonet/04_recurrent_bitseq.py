from evolib import Population, Individual, FitnessFunction, plot_approximation
from evolib.representation.evonet import EvoNet
import matplotlib.pyplot as plt
import numpy as np

FRAME_FOLDER = "04_frames_point"

input_seq = [0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1] * 4
target_seq = [1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0] * 4
warmup_steps = 11


def fitness_bitseq(indiv: Individual) -> float:
    """
    Evaluate how well the EvoNet predicts the next bit in a fixed sequence.
    """
    net: EvoNet = indiv.para["brain"].net
    net.reset(full=True)

    total_error = 0.0
    for t in range(len(input_seq)):
        output = net.calc([input_seq[t]])[0]
        if t >= warmup_steps:
            error = output - target_seq[t]
            total_error += error**2
    
    return total_error / (len(input_seq) - warmup_steps)


def save_plot(pop: Population):
    """
    Plot network predictions vs target values over time.
    """
    best = pop.best()
    y_preds = [best.para["brain"].net.calc([bit])[0] for bit in input_seq]

    plot_approximation(
        y_preds,
        target_seq,
        title=f"Bit Prediction over Time (gen={pop.generation_num}, "
        f"MSE={best.fitness:.4f})",
        pred_label="Prediction",
        show=False,
        show_grid=False,
        save_path=f"{FRAME_FOLDER}/gen_{pop.generation_num:03d}.png",
        y_limits=(-0.2, 1.2),
        true_marker="o",
        pred_marker="o",
        true_lw=0,
        pred_lw=1,
        true_ls="",
        pred_ls="",
    )

    print(pop.mu)


if __name__ == "__main__":
    pop = Population("configs/04_recurrent_bitseq.yaml", 
                     fitness_function = fitness_bitseq)
    pop.run(verbosity=1, on_generation_end=save_plot)
#    pop.run(verbosity=2)

