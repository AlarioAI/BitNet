import json
import numpy as np
import re

from bitnet.config import ProjectConfig


def generate_latex_table_and_graph(results):
    header = "\\begin{table}[h]\n" \
             "\\centering\n" \
             "\\begin{tabular}{|c|c|c|c|c|}\n" \
             "\\Xhline{2\\arrayrulewidth}\n" \
             "\\textbf{Architecture} & \\textbf{Dataset} & \\textbf{Type} & \\textbf{Mean Accuracy (\\%)} & \\textbf{Std Dev (\\%)} \\\\\n" \
             "\\Xhline{2\\arrayrulewidth}\n"
    footer = "\\end{tabular}\n" \
             "\\caption{Experimental Results Comparing BitNet and FloatNet across various architectures and datasets.}\n" \
             "\\label{tab:results}\n" \
             "\\end{table}\n\n"

    body = ""
    plot_data = ""
    for experiment, models in results.items():
        dataset, architecture = experiment.split('_')
        bitnet_data = models.get('BitNet', {})
        floatnet_data = models.get('FloatNet', {})
        mean_bitnet = np.mean(bitnet_data.get('scores', [0]))
        mean_floatnet = np.mean(floatnet_data.get('scores', [0]))
        std_bitnet = np.std(bitnet_data.get('scores', [0]))
        std_floatnet = np.std(floatnet_data.get('scores', [0]))
        num_params = bitnet_data.get('num_parameters', 0)

        discrepancy = abs(mean_bitnet - mean_floatnet)

        # Data for the scatter plot
        plot_data += f"({num_params}, {discrepancy}) "

        # Compare scores and bold the best
        mean_accuracy_bitnet = f"\\textbf{{{mean_bitnet:.2f}}}" if mean_bitnet > mean_floatnet else f"{mean_bitnet:.2f}"
        mean_accuracy_floatnet = f"\\textbf{{{mean_floatnet:.2f}}}" if mean_floatnet > mean_bitnet else f"{mean_floatnet:.2f}"

        body += f"{architecture} & {dataset} & BitNet & {mean_accuracy_bitnet} & {std_bitnet:.2f} \\\\\n"
        body += f"{architecture} & {dataset} & FloatNet & {mean_accuracy_floatnet} & {std_floatnet:.2f} \\\\\n"
        body += "\\Xhline{2\\arrayrulewidth}\n"

    # Add the scatter plot to the footer
    graph_footer = "\\begin{figure}[h]\n" \
                   "\\centering\n" \
                   "\\begin{tikzpicture}\n" \
                   "\\begin{axis}[\n" \
                   "xlabel={Number of Parameters},\n" \
                   "ylabel={Accuracy Discrepancy},\n" \
                   "]\n" \
                   "\\addplot[only marks] coordinates {\n" \
                   f"{plot_data}\n" \
                   "};\n" \
                   "\\end{axis}\n" \
                   "\\end{tikzpicture}\n" \
                   "\\caption{Correlation between number of parameters and accuracy discrepancy for BitNet and FloatNet.}\n" \
                   "\\label{fig:discrepancy_plot}\n" \
                   "\\end{figure}\n"

    return f"{header}{body}{footer}{graph_footer}"





def insert_table_into_document(document_path, table_data):
    with open(document_path, 'r') as file:
        content = file.read()

    pattern = r'% BEGIN_TABLE.*?% END_TABLE'
    replacement = f'% BEGIN_TABLE\n{table_data}\n% END_TABLE'
    # Ensure all backslashes in the replacement text are escaped properly
    replacement = replacement.replace('\\', '\\\\')
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(document_path, 'w') as file:
        file.write(new_content)


def main():
    results_file = ProjectConfig.RESULTS_FILE
    latex_document_path = ProjectConfig.PAPER_TEX_PATH

    with open(results_file, 'r') as f:
        results = json.load(f)

    table_data = generate_latex_table_and_graph(results)
    insert_table_into_document(latex_document_path, table_data)


if __name__ == '__main__':
    main()