import numpy as np
import matplotlib.pyplot as plt

from GENetLib.fda_func import eval_fd


"""Plot functions fitting from densely measured observations"""


def plot_rawdata(
    location,
    X,
    color=None,
    pch=4,
    cex=0.9,
    show_legend=True,
    title=None,
    grid=False,
    figsize=(8, 6),
):
    n, m = X.shape
    type_ = "o"
    truelengths = np.sum(~np.isnan(X))
    plt.figure(figsize=figsize)
    if truelengths == n * m:
        if color is None:
            plt.plot(location, X.T, marker=type_, markersize=pch, label="X")
        else:
            plt.plot(
                location,
                X.T,
                marker=type_,
                markersize=pch,
                color=color,
                label="X",
            )
    else:
        location_list = []
        X_list = []
        for i in range(n):
            mask = ~np.isnan(X[i, :])
            location_list.append(location[mask])
            X_list.append(X[i, mask])
        if color is None:
            for i in range(n):
                plt.plot(
                    location_list[i],
                    X_list[i],
                    marker=type_,
                    markersize=pch,
                    label=f"X{i+1}",
                )
        else:
            for i in range(n):
                plt.plot(
                    location_list[i],
                    X_list[i],
                    marker=type_,
                    markersize=pch,
                    color=color,
                    label=f"X{i+1}",
                )
    plt.xlabel("Location")
    plt.ylabel("X")
    if title is not None:
        plt.title(title)
    if grid:
        plt.grid(True)
    if show_legend:
        plt.legend()
    plt.show()


"""Plot functional objects"""


def plot_fd(
    x,
    y=None,
    xlab=None,
    ylab=None,
    title=None,
    colors=None,
    linestyles=None,
    legend=None,
    grid=False,
    figsize=(8, 6),
):
    fdobj = x
    coef = fdobj["coefs"]
    coefd = coef.shape
    nbasis = coefd[0]
    nx = np.max([501, 10 * nbasis + 1])
    nrep = coefd[1]
    basisobj = fdobj["basis"]
    rangex = basisobj["rangeval"]
    if y is None:
        y = nx
    if y >= 1:
        y = list(np.linspace(rangex[0], rangex[1], num=int(y)))
    else:
        raise ValueError("'y' is a single number less than one.")
    xlim = rangex
    fdmat = eval_fd(y, fdobj, 0)
    rangey = [np.min(fdmat), np.max(fdmat)]
    ylim = rangey
    plt.figure(figsize=figsize)
    for irep in range(nrep):
        color = (
            colors[irep] if colors is not None and irep < len(colors) else None
        )
        linestyle = (
            linestyles[irep]
            if linestyles is not None and irep < len(linestyles)
            else "-"
        )
        plt.plot(
            y,
            fdmat[:, irep],
            color=color,
            linestyle=linestyle,
            label=(
                legend[irep]
                if legend is not None and irep < len(legend)
                else None
            ),
        )
    plt.axhline(0, linestyle="--", color="black")
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    if title is not None:
        plt.title(title)
    if legend is not None:
        plt.legend()
    if grid:
        plt.grid(True)
    plt.show()
