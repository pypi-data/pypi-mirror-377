# from os import listdir
from os.path import join, dirname, pardir
from copy import deepcopy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import get_scorer
from umap import UMAP
from mlresearch.latex import (
    make_mean_sem_table,
    export_longtable,
    make_bold,
    format_table,
)
from mlresearch.utils import set_matplotlib_style

import sys

PROJ_PATH = join(dirname(__file__), pardir)
sys.path.append(PROJ_PATH)

# Retrieve metrics used
from experiments.results_sbert import CONFIG  # noqa

DATA_PATH = join(dirname(__file__), "data")
RESULTS_PATH = join(dirname(__file__), "results")
ANALYSIS_PATH = join(dirname(__file__), "analysis")

set_matplotlib_style(font_size=30)

LLAMA_HAZARD_CATEGORIES = {
    "safe": "Safe",
    "S1": "Violent Crimes",
    "S2": "Non-Violent Crimes",
    "S3": "Sex-Related Crimes",
    "S4": "Child Sexual Exploitation",
    "S5": "Defamation",
    "S6": "Specialized Advice",
    "S7": "Privacy",
    "S8": "Intellectual Property",
    "S9": "Indiscriminate Weapons",
    "S10": "Hate",
    "S11": "Suicide & Self-Harm",
    "S12": "Sexual Content",
    "S13": "Elections",
    "S14": "Code Interpreter Abuse",
}
MODEL_NAMES_MAPPER = {
    "meta-llama-Meta-Llama-3.1-8B-Instruct": "Base",
    "Orenguteng-Llama-3.1-8B-Lexi-Uncensored-V2": "Uncensored",
}
DATASET_NAMES_MAPPER = {"advbench": "Advbench", "ifeval": "IFEval"}


def _format_dataset(row):
    if row["Dataset"] == "A":
        return "A"
    elif row["Dataset"] == "B" and row.name.startswith("HBI"):
        return "B"
    else:
        return "A|B"


def get_mean_sem_results(results):
    results = results.groupby("param_est_name").apply(
        lambda df: df.iloc[df["mean_test_f1"].argmax()], include_groups=False
    )
    mean_sem = []
    for ms in ["mean_test_", "std_test_"]:
        columns = [
            *results.columns[results.columns.str.startswith(ms)].tolist(),
        ]
        res_ = deepcopy(results)[columns]
        res_.columns = res_.columns.str.replace(ms, "")
        mean_sem.append(res_)
    return mean_sem


def format_all_perf(all_perf):
    all_perf = pd.concat(all_perf)
    all_perf["Dataset"] = all_perf.apply(_format_dataset, axis=1)
    all_perf["Model"] = all_perf.apply(lambda x: x.name.split("|")[-1], axis=1)
    all_perf.reset_index(drop=True, inplace=True)
    all_perf.columns = all_perf.columns.str.title()
    all_perf.sort_values("Dataset", inplace=True)
    all_perf = all_perf[["Dataset", "Model", *all_perf.columns[:-2]]]
    return all_perf


def get_oos_performance_score(results, threshold=0.5):
    results = results.copy()
    results = (results > threshold).astype(int)
    target = results.target

    metrics = CONFIG["SCORING"]
    metrics = {m: get_scorer(m)._score_func for m in metrics}
    results = pd.DataFrame(
        {m: results.apply(lambda col: metrics[m](col, target)) for m in metrics.keys()}
    )
    results["Dataset"] = "B"
    results["Dataset"] = results.apply(lambda row: _format_dataset(row)[0], axis=1)
    results["Model"] = results.apply(lambda x: x.name.split("|")[-1], axis=1)
    results.sort_values("Dataset", inplace=True)
    results = results[["Dataset", "Model", *results.columns[:-2]]]
    return results


def make_oos_line_chart(results, true_target=0, ax=None):
    results = results.copy()
    target = results.target
    results.drop(columns="target", inplace=True)

    taus = np.linspace(0, 1, num=101)
    pass_perc = {tau: (results[target == true_target] > tau).mean() for tau in taus}

    pass_perc = pd.DataFrame(pass_perc).T
    ax = pass_perc.plot.line(ax=ax)
    return ax


if __name__ == "__main__":

    # Hidden states scatter plot projection
    df_emb = pd.read_pickle(join(RESULTS_PATH, "sbert_embeddings.pkl"))
    source = (
        ["Harmful" for _ in range(1300)]
        + ["Benign" for _ in range(1300)]
        + ["IFEval" for _ in range(1300)]
    )
    df_emb.drop(columns="response_type", inplace=True)
    embedding = UMAP(
        n_components=2, metric="euclidean", random_state=42, verbose=True, n_jobs=1
    ).fit(df_emb)
    df_emb = pd.DataFrame(embedding.embedding_, columns=["x", "y"])
    df_emb["source"] = source
    sns.scatterplot(data=df_emb, x="x", y="y", hue="source", s=50, linewidth=0.01)
    plt.legend(
        loc="lower center",
        ncol=3,
        bbox_to_anchor=(0, 0.95, 1, 0.5),
    )
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.ylim(top=18)
    plt.xlim(left=2)
    plt.savefig(
        join(ANALYSIS_PATH, "umap_projections_train_data.pdf"),
        format="pdf",
        bbox_inches="tight",
        transparent=True,
    )
    plt.close()

    # Redefine RCParams for lineplots
    set_matplotlib_style(font_size=30, **{"lines.linewidth": 5})

    for ctg_version in ["sbert", "hidden_states_truncated"]:
        # K-fold / Parameter tuning results
        all_perf = []
        for dataset in ["A", "B"]:
            results = pd.read_pickle(
                join(
                    RESULTS_PATH,
                    f"param_tuning_results_dataset_{dataset}_{ctg_version}.pkl",
                )
            )
            mean_sem_results = get_mean_sem_results(results)
            perf_table = make_mean_sem_table(
                *mean_sem_results, make_bold=True, decimals=3, axis=0
            )
            perf_table["Dataset"] = dataset
            all_perf.append(perf_table)

        all_perf = format_all_perf(all_perf)
        export_longtable(
            all_perf,
            path=join(ANALYSIS_PATH, f"kfold_results_{ctg_version}.tex"),
            caption="""
            Classifier performance results after parameter tuning over 10-fold cross
            validation.
            """,
            label="tbl:kfold-results",
            index=False,
        )

        # Analyze OOS results
        # fig, axes = plt.subplots(1, 4, sharey=True, figsize=(6, 2))
        # i = 0
        metrics = {}
        results = pd.read_pickle(
            join(RESULTS_PATH, f"out_of_sample_results_llama_{ctg_version}.pkl")
        )
        results = results[
            results.columns[results.columns.str.startswith("HBI")].tolist() + ["target"]
        ]
        results.columns = results.columns.str.replace("HBI|DROP|", "")
        results.drop(columns="CONSTANT", inplace=True)

        # Line charts for benign and dangerous
        for true_target in range(2):
            target_type = "dangerous" if true_target else "benign"
            make_oos_line_chart(results, true_target=true_target)  # , ax=axes[i]

            plt.ylabel(r"Flagged as unsafe (\%)")
            plt.xlabel(r"$\tau$")
            plt.legend(
                labels=results.columns.drop("target"),
                loc="lower center",
                ncol=2,
                bbox_to_anchor=(0, 0.95, 1, 0),
            )
            plt.savefig(
                join(ANALYSIS_PATH, f"linechart_{target_type}_llama_{ctg_version}.pdf"),
                format="pdf",
                bbox_inches="tight",
                transparent=True,
            )
            plt.close()
            # axes[i].legend([])
            # axes[i].set_xlabel(f"Llama / {target_type}")
            # i += 1

        # Get performance scores for given threshold (as a table)
        threshold = 0.5
        oos_performance = get_oos_performance_score(results, threshold=threshold)
        oos_performance = make_bold(
            oos_performance.set_index(["Dataset", "Model"]), axis=0
        )
        export_longtable(
            oos_performance.reset_index(),
            path=join(ANALYSIS_PATH, f"oos_performance_llama_{ctg_version}.tex"),
            caption=f"""
            Classifier performance results after parameter tuning over an out-of-sample
            dataset with responses generated by Llama
            ($\\tau = {threshold}$).
            """,
            label="tbl:oos-performance-llama",
            index=False,
        )

        # axes[0].set_ylabel(r"Rejection (%)")
        # fig.legend(
        #     labels=results.columns.drop("target"),
        #     loc="lower center",
        #     ncol=results.columns.size-1,
        #     bbox_to_anchor=(0, 0.9, 1, 0.5)
        # )
        # plt.savefig(
        #     join(ANALYSIS_PATH, "linechart_oos_all.pdf"),
        #     format="pdf",
        #     bbox_inches="tight",
        #     transparent=True
        # )

        # Get scores over tokens for G
        df_time_scores = pd.read_pickle(
            join(RESULTS_PATH, f"oos_time_scores_{ctg_version}.pkl")
        )
        df_time_scores = (
            df_time_scores.drop(columns="response").melt(["response_type"]).dropna()
        )
        df_time_scores["response_type"] = df_time_scores["response_type"].map(
            {0.0: "Normal", 1.0: "Jailbroken"}
        )
        sns.lineplot(
            df_time_scores[df_time_scores["variable"] < 100],
            x="variable",
            y="value",
            hue="response_type",
        )
        plt.xlabel("Token generated at time step t")
        plt.ylabel(r"$G(\mathbf{y}_{\leq t})$")
        plt.legend(
            loc="lower center",
            ncol=results.columns.size - 1,
            bbox_to_anchor=(0, 0.95, 1, 0),
        )
        plt.savefig(
            join(
                ANALYSIS_PATH,
                f"linechart_scores_over_tokens_oos_100_each_type_{ctg_version}.pdf",
            ),
            format="pdf",
            bbox_inches="tight",
            transparent=True,
        )
        plt.close()

        ################################################################################
        # Evaluation responses analysis
        ################################################################################
        df_results = pd.read_csv(join(RESULTS_PATH, "final_results_table_may13.csv"))
        df_results["inference_p_token"] = (
            df_results["inference_time"] / df_results["num_of_tokens"]
        )
        df_results.drop(columns="Unnamed: 0", inplace=True)

        df_results["model"] = df_results["model"].map(MODEL_NAMES_MAPPER)
        df_results["dataset"] = df_results["dataset"].map(DATASET_NAMES_MAPPER)

        # Extract categories for llamaguard prompt evaluations
        df_results["category"] = (
            df_results["llamaguard_prompt"]
            .apply(lambda x: x.split("\n")[-1])
            .map(LLAMA_HAZARD_CATEGORIES)
        )

        # safe_ctg_unc = df_results[
        #     (df_results["model"] == "Orenguteng-Llama-3.1-8B-Lexi-Uncensored-V2")
        #     & (df_results["unsafe"] == 0)
        #     & (df_results["method"] == "ctg")
        # ].prompt
        # unsafe_orig_unc = df_results[
        #     (df_results["model"] == "Orenguteng-Llama-3.1-8B-Lexi-Uncensored-V2")
        #     & (df_results["unsafe"] == 1)
        #     & (df_results["method"] == "original")
        # ].prompt
        # disagreement_prompts = set(safe_ctg_unc) & set(unsafe_orig_unc)

        df_results["method"] = df_results["method"].map(
            {
                "tokenmasking": "c-FUDGE",
                "original": "Vanilla",
                "ctg": "CTG",
                "self_reflect": "Self-reflect",
                "wildguardctg": "WildguardCTG",
            }
        )
        df_ifeval = df_results[["dataset", "model", "method", "ifeval_loose"]].copy()
        df_results.drop(columns=["ifeval_strict", "ifeval_loose"], inplace=True)

        # Export IFEval performance
        df_ifeval = df_ifeval[df_ifeval["dataset"] == "IFEval"].drop(columns="dataset")
        df_ifeval = df_ifeval.groupby(["model", "method"]).mean().reset_index()
        df_ifeval = df_ifeval.pivot(
            columns="model", index="method", values="ifeval_loose"
        )
        df_ifeval.to_excel(join(ANALYSIS_PATH, "results_ifeval_performance.xlsx"))

        # Export results overall
        df_overall = (
            df_results.groupby(["model", "method", "dataset"])
            .mean(numeric_only=True)[
                [
                    "wildguard_unsafe",
                    "llamaguard_unsafe",
                    "ppl_score",
                    "inference_p_token",
                ]
            ]
            .reset_index()
            .rename(
                columns={
                    "wildguard_unsafe": "WildGuard",
                    "llamaguard_unsafe": "LlamaGuard",
                    "ppl_score": "Perplexity",
                    "inference_p_token": "Inference time",
                    "model": "Model",
                    "method": "Method",
                }
            )
            .pivot(
                columns=["Model"],
                index=["dataset", "Method"],
                values=["WildGuard", "LlamaGuard", "Perplexity", "Inference time"],
            )
            .T
        )
        df_overall.index.names = ["Metric", "Llama"]

        df_overall_all = df_overall.copy()
        for dataset_name in ["Advbench", "IFEval"]:
            df_overall = df_overall_all[dataset_name].copy()

            df_ifeval_temp = df_ifeval.T.reset_index().rename(
                columns={"model": "Llama"}
            )
            df_ifeval_temp["Metric"] = "IFEval Perf."
            df_ifeval_temp.set_index(["Metric", "Llama"], inplace=True)
            df_overall = pd.concat([df_overall, df_ifeval_temp])
            df_overall = (
                df_overall.reset_index().set_index(["Llama", "Metric"]).sort_index()
            )
            df_overall = format_table(
                df_overall,
                indices=[
                    {"Base": "Base", "Uncensored": "Uncensored"},
                    {
                        "WildGuard": "WildGuard Unsafeness",
                        "LlamaGuard": "LlamaGuard Unsafeness",
                        "IFEval Perf.": "IFEval Performance",
                        "Perplexity": "Perplexity",
                        "Inference time": "Inference time",
                    },
                ],
                columns=[],
                drop_missing=False,
            )
            df_overall = df_overall[
                ["Vanilla", "c-FUDGE", "Self-reflect", "CTG", "WildguardCTG"]
            ].round(3)
            df_overall.to_excel(
                join(ANALYSIS_PATH, f"results_overall_{dataset_name}.xlsx")
            )

        # Export results per category
        for model in df_results.model.unique():
            df_categories = (
                df_results[df_results["model"] == model]
                .groupby(["category", "method"])
                .mean(numeric_only=True)[
                    [
                        "wildguard_unsafe",
                        "llamaguard_unsafe",
                        "ppl_score",
                        "inference_p_token",
                    ]
                ]
                .reset_index()
                .rename(
                    columns={
                        "wildguard_unsafe": "WildGuard",
                        "llamaguard_unsafe": "LlamaGuard",
                        "ppl_score": "Perplexity",
                        "inference_p_token": "Inference time",
                        "category": "Category",
                        "method": "Method",
                    }
                )
                .pivot(
                    columns=["Method"],
                    index=["Category"],
                    values=["WildGuard", "LlamaGuard", "Perplexity", "Inference time"],
                )
                .T
            )
            df_categories.index.names = ["Metric", "Method"]
            df_categories = format_table(
                df_categories,
                indices=[
                    ["WildGuard", "LlamaGuard", "Perplexity", "Inference time"],
                    ["Vanilla", "c-FUDGE", "Self-reflect", "CTG"],
                ],
                columns=[],
                drop_missing=False,
            ).T.round(3)
            # for col in df_categories.columns.get_level_values(0).unique():
            #     df_categories[col] = make_bold(
            #         df_categories[col], maximum=False, decimals=3
            #     )
            counts = df_results.drop_duplicates("prompt").groupby(["category"]).size()
            df_categories["Freq."] = counts
            df_categories.drop("Safe", inplace=True)
            df_categories = df_categories[df_categories["Freq."] > 10].T
            df_categories.to_excel(
                join(ANALYSIS_PATH, f"results_per_category_{model}.xlsx")
            )
