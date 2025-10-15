import argparse

import matplotlib.colors as colors
import matplotlib.pyplot as plt
import mosaic
import xarray as xr


def plot_var_comparison(file1, file2, var, output_file=None, show_plot=False):
    # Load both datasets
    ds1 = xr.open_dataset(file1)
    ds2 = xr.open_dataset(file2)

    # Safety checks
    for name, ds in zip(["File 1", "File 2"], [ds1, ds2]):
        if var not in ds:
            raise ValueError(f"{name} does not contain '{var}' field.")

    var1 = ds1[var][0, :]
    var2 = ds2[var][0, :]
    if var == 'surfaceSpeed':
        var1 *= 3.15e7
        var2 *= 3.15e7
    diff = var2 - var1

    # Create the figure with 3 subplots
    fig, axes = plt.subplots(ncols=3, figsize=(18, 6), constrained_layout=True,
                             sharex=True, sharey=True)

    print(f'var1: min={var1.min().item()}, max={var1.max().item()}')
    print(f'var2: min={var2.min().item()}, max={var2.max().item()}')
    if var == 'surfaceSpeed':
        vmin = 1.0
        vmax = max(var1.max().item(), var2.max().item())
    else:
        vmin = min(var1.min().item(), var2.min().item())
        vmax = max(var1.max().item(), var2.max().item())
    print(f'combined: {vmin}, {vmax}')
    norm = colors.LogNorm(vmin=vmin, vmax=vmax)

    # assume we can use mesh from ds1 for both
    descriptor = mosaic.Descriptor(ds1)

    # Plot variable from file 1
    pc = mosaic.polypcolor(
        axes[0], descriptor, var1, aa=False,
        norm=norm)
    fig.colorbar(pc, ax=axes[0], fraction=0.1, label=f"{var}")
    axes[0].set_title(f"{var}: File 1")

    # Plot variable from file 2
    pc = mosaic.polypcolor(
        axes[1], descriptor, var2, aa=False,
        norm=norm)
    fig.colorbar(pc, ax=axes[1], fraction=0.1, label=f"{var}")
    axes[1].set_title(f"{var}: File 2")

    # Plot the difference
    diff_vmax = max(abs(diff.min().item()), abs(diff.max().item()))
    norm_diff = colors.SymLogNorm(linthresh=0.5, linscale=0.5,
                                  vmin=-diff_vmax, vmax=diff_vmax, base=10)
    pc = mosaic.polypcolor(
        axes[2], descriptor, diff, aa=False,
        norm=norm_diff, cmap='RdBu_r')
    fig.colorbar(pc, ax=axes[2], fraction=0.1, label=f"{var} diff")
    axes[2].set_title("Difference")

    for ax in axes:
        ax.set_aspect('equal')
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")

    # Save or show
    if output_file:
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {output_file}")
    if show_plot:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Compare muFriction from two MALI "
        "input files using mosaic.")
    parser.add_argument("file1",
                        help="Path to the first MALI input NetCDF file.")
    parser.add_argument("file2",
                        help="Path to the second MALI input NetCDF file.")
    parser.add_argument("--var",
                        help="variable to plot")
    parser.add_argument("--output",
                        help="Output image file "
                        "(e.g., muFriction_comparison.png).")
    parser.add_argument("--show", action="store_true",
                        help="Show the plot interactively.")

    args = parser.parse_args()
    plot_var_comparison(args.file1, args.file2, args.var,
                        args.output, args.show)
