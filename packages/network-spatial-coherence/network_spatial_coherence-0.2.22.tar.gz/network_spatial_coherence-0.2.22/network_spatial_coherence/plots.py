import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
from curve_fitting import CurveFitting
import seaborn as sns
import matplotlib.cm as cm
import matplotlib.colors as mcolors



import scienceplots
import os
from scipy.interpolate import griddata
import json
from scipy.spatial.distance import pdist

from algorithms import find_geometric_central_node, compute_shortest_path_mapping_from_central_node
from map_image_to_colors import map_points_to_colors






def plot_spatial_constant(args, df):
    plt.figure()

    # Plot Spatial Constant
    plt.plot(df['number_of_random_edges'], df['K_sp'], marker='o', label='Spatial Constant', color='tab:blue')

    # Plot Small-World Constant
    plt.plot(df['number_of_random_edges'], df['K_smallworld'], marker='x', label='Small-World Constant', color='tab:red')

    # Set labels and title
    plt.xlabel('Number of Random Edges Added')
    plt.ylabel('Constant')
    plt.title('Spatial and Small-World Constants vs. Number of Random Edges')

    plt.legend()

    # Title and grid
    plt.title('Spatial and Small-World Constants vs. Number of Random Edges')


    # Save the plot
    save_path = args.directory_map['plots_spatial_constant']
    plt.savefig(f"{save_path}/spatial_constant_change_with_false_edges_data.png")
    if args.show_plots:
        plt.show()
        plt.close()

def plot_average_shortest_path(args, df):
    plt.figure()

    # Plot Average Shortest Path Length
    plt.plot(df['number_of_random_edges'], df['mean_shortest_path'], marker='o', color='tab:green')

    # Set labels and title
    plt.xlabel('Number of Random Edges Added')
    plt.ylabel('Average Shortest Path Length')
    plt.title('Average Shortest Path Length vs. Number of Random Edges Added')

    # Save the plot
    save_path = args.directory_map['plots_spatial_constant']
    plt.savefig(f"{save_path}/average_shortest_path_vs_random_edges.png")
    if args.show_plots:
        plt.show()
        plt.close()





def plot_mean_sp_with_graph_growth(args, df, plot_filename, model="spatial_constant_dim=2", return_s_and_r2=False):
    # Initialize GraphFitting instance with the data
    curve_fitting = CurveFitting(df['num_nodes'].values, df['mean_shortest_path'].values)
    print(model)
    if model == "spatial_constant_dim=2":
        model_func = curve_fitting.spatial_constant_dim2
    elif model == "spatial_constant_dim=3":
        model_func = curve_fitting.spatial_constant_dim3
    elif model == "spatial_constant_dim=2_linearterm":
        model_func = curve_fitting.spatial_constant_dim2_linearterm
    elif model == "spatial_constant_dim=3_linearterm":
        model_func = curve_fitting.spatial_constant_dim3_linearterm


    elif model == "power_model_2d_Sconstant":
        model_func = curve_fitting.power_model_2d_Sconstant
    elif model == "power_model_3d_Sconstant":
        model_func = curve_fitting.power_model_3d_Sconstant
    elif model == "power_model_2d_bi_Sconstant":
        model_func = curve_fitting.power_model_2d_bi_Sconstant
    elif model == "power_model_3d_bi_Sconstant":
        model_func = curve_fitting.power_model_3d_bi_Sconstant


    elif model == "small_world":
        model_func = curve_fitting.small_world_model
    elif model == "power_law":
        model_func = curve_fitting.power_model
    elif model == "power_law_w_constant":
        model_func = curve_fitting.power_model_w_constant

    # Perform curve fitting using the power model
    curve_fitting.perform_curve_fitting(model_func)

    # Set labels, title, and save path
    xlabel = 'Number of Nodes'
    ylabel = 'Mean Shortest Path'
    title = 'Mean Shortest Path vs. Number of Nodes'
    save_path = f"{args.directory_map['plots_spatial_constant_gg']}/{plot_filename}"

    # Plot the data with the fitted curve
    curve_fitting.plot_fit_with_uncertainty(model_func, xlabel, ylabel, title, save_path)
    if return_s_and_r2:
        return curve_fitting.popt[0], curve_fitting.r_squared  # return spatial constant and r2
    else:
        return




def plot_mean_sp_with_num_nodes_large_and_smallworld(args, df, plot_filename):
    fig, ax = plt.subplots(figsize=(12, 8), dpi=100)


    series_types = df['series_type'].unique()
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    for series, color in zip(series_types, colors):
        if series == "Original" or series == "Smallworld":
            continue
        df_series = df[df['series_type'] == series]

        x_data = df_series['num_nodes'].values
        y_data = df_series['mean_shortest_path'].values
        sorted_indices = np.argsort(x_data)
        sorted_x = x_data[sorted_indices]
        sorted_y = y_data[sorted_indices]


        ax.scatter(sorted_x, sorted_y,  alpha=0.5, edgecolors='w', zorder=3, color=color)
        plt.plot(sorted_x, sorted_y, label=series,
                 linestyle='--', color=color, zorder=2)



    # Plot for Original Graph
    df_original = df[df['series_type'] == "Original"]
    curve_fitting_original = CurveFitting(df_original['num_nodes'].values, df_original['mean_shortest_path'].values)
    if args.dim == 2:
        func_fit = curve_fitting_original.spatial_constant_dim2
    elif args.dim == 3:
        func_fit = curve_fitting_original.spatial_constant_dim3
    else:
        raise ValueError("Dimension must be 2 or 3")
    curve_fitting_original.plot_fit_with_uncertainty_for_dataset(df_original['num_nodes'].values,
                                                                 df_original['mean_shortest_path'].values,
                                                                 func_fit,
                                                                 ax, label_prefix='Original', color='tab:blue',
                                                                 y_position=0.95)
    print("STD parameters Original", curve_fitting_original.sigma)

    # Plot for Small-World Graph
    df_small_world =  df[df['series_type'] == "Smallworld"]
    curve_fitting_small_world = CurveFitting(df_small_world['num_nodes'].values, df_small_world['mean_shortest_path'].values)
    curve_fitting_small_world.plot_fit_with_uncertainty_for_dataset(df_small_world['num_nodes'].values,
                                                                    df_small_world['mean_shortest_path'].values,
                                                                    curve_fitting_small_world.power_model, ax,
                                                                    label_prefix='Small-World', color='tab:red',
                                                                    y_position=0.85)

    print("STD parameters SmallWorld", curve_fitting_small_world.sigma)

    # Set labels and title
    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel('Mean Shortest Path')
    ax.set_title('Mean Shortest Path vs. Number of Nodes')
    ax.legend()

    # Save the plot
    save_path = f"{args.directory_map['plots_spatial_constant']}/{plot_filename}"
    plt.savefig(save_path)



def plot_clustering_coefficient_distribution(args, clustering_coefficients, title="Clustering Coefficient Distribution"):
    plt.figure(figsize=(12, 6))  # Adjusted figure size for potential subplots

    if args.is_bipartite:
        # Plotting two subplots for each set in a bipartite graph
        mean_clustering_coefficient_set1 = args.mean_clustering_coefficient_set1
        mean_clustering_coefficient_set2 = args.mean_clustering_coefficient_set2

        # Clustering Coefficients for Set 1
        plt.subplot(1, 2, 1)  # First subplot in a 1x2 grid
        plt.hist(clustering_coefficients[0], bins=20, color='blue', alpha=0.7, rwidth=0.85)
        plt.title(title + " - Set 1")
        plt.xlabel('Clustering Coefficient')
        plt.ylabel('Frequency')
        plt.legend([f"Mean Clustering Coefficient: {mean_clustering_coefficient_set1:.2f}"])

        # Clustering Coefficients for Set 2
        plt.subplot(1, 2, 2)  # Second subplot in a 1x2 grid
        plt.hist(clustering_coefficients[1], bins=20, color='red', alpha=0.7, rwidth=0.85)
        plt.title(title + " - Set 2")
        plt.xlabel('Clustering Coefficient')
        plt.ylabel('Frequency')
        plt.legend([f"Mean Clustering Coefficient: {mean_clustering_coefficient_set2:.2f}"])

    else:
        # Plotting a single histogram for non-bipartite graphs
        mean_clustering_coefficient = args.mean_clustering_coefficient
        plt.hist(clustering_coefficients, bins=20, color='blue', alpha=0.7, rwidth=0.85)
        plt.title(title)
        plt.xlabel('Clustering Coefficient')
        plt.ylabel('Frequency')
        plt.legend([f"Mean Clustering Coefficient: {mean_clustering_coefficient:.2f}"])

    plot_folder = args.directory_map['plots_clustering_coefficient']
    plt.savefig(f"{plot_folder}/clust_coef_{args.args_title}", format="png")
    if args.show_plots:
        plt.show()
        plt.close()



def plot_degree_distribution(args, degree_distribution, title="Degree Distribution"):
    plt.figure(figsize=(12, 6))  # Adjusted figure size for potential subplots

    if args.is_bipartite:
        # Plotting two subplots for each set in a bipartite graph
        average_degree_set1 = args.average_degree_set1
        average_degree_set2 = args.average_degree_set2

        # Degree Distribution for Set 1
        plt.subplot(1, 2, 1)  # First subplot in a 1x2 grid
        plt.bar(range(len(degree_distribution[0])), degree_distribution[0], color='blue', alpha=0.7)
        plt.title(title + " - Set 1")
        plt.xlabel('Degree')
        plt.ylabel('Frequency')
        plt.legend([f"Average Degree: {average_degree_set1:.2f}"])

        # Degree Distribution for Set 2
        plt.subplot(1, 2, 2)  # Second subplot in a 1x2 grid
        plt.bar(range(len(degree_distribution[1])), degree_distribution[1], color='red', alpha=0.7)
        plt.title(title + " - Set 2")
        plt.xlabel('Degree')
        plt.ylabel('Frequency')
        plt.legend([f"Average Degree: {average_degree_set2:.2f}"])

    else:
        # Plotting a single bar chart for non-bipartite graphs
        average_degree = args.average_degree
        plt.bar(range(len(degree_distribution)), degree_distribution, color='green', alpha=0.7)
        plt.title(title)
        plt.xlabel('Degree')
        plt.ylabel('Frequency')
        plt.legend([f"Average Degree: {average_degree:.2f}"])

    plot_folder = args.directory_map['plots_degree_distribution']
    print(args.args_title)
    plt.savefig(f"{plot_folder}/degree_dist_{args.args_title}", format="png")
    if args.show_plots:
        plt.show()
    plt.close()

def plot_shortest_path_distribution(args, shortest_path_dist, mean_shortest_path, title="Shortest Path Distribution"):
    # Plotting a single bar chart for non-bipartite graphs
    plt.figure(figsize=(12, 6))  # Adjusted figure size for potential subplots
    unique_paths, counts = np.unique(shortest_path_dist, return_counts=True)
    plt.bar(unique_paths, counts, color='blue', alpha=0.7)

    # Add a vertical line for the mean shortest path
    plt.axvline(x=mean_shortest_path, color='red', linestyle='--', linewidth=2, label=f"Mean: {mean_shortest_path:.2f}")

    plt.title(title)
    plt.xlabel('Shortest Path')
    plt.ylabel('Frequency')
    plt.legend()

    plot_folder = args.directory_map['plots_shortest_path_distribution']
    plt.savefig(f"{plot_folder}/plots_shortest_path_distribution_{args.args_title}", format="png")
    if args.show_plots:
        plt.show()
    plt.close()



### Functions for spatial constant variation analysis



def classify_row(row):
    if row['dim'] == 2 and 'bipartite' not in row['proximity_mode']:
        return '2D Non-Bipartite'
    elif row['dim'] == 2 and 'bipartite' in row['proximity_mode']:
        return '2D Bipartite'
    elif row['dim'] == 3 and 'bipartite' not in row['proximity_mode']:
        return '3D Non-Bipartite'
    else:  # row['dim'] == 3 and 'bipartite' in row['proximity_mode']
        return '3D Bipartite'

def plot_spatial_constant_variation(args, spatial_constant_variation_results_df):
    # quantity_of_interest = "S_general" # spatial constant
    quantity_of_interest = "relative_msp_prediction_error"
    ### Predictions
    constant_scaler = np.sqrt(4.5)
    bipartite_correction = 1 / 1.2  # 1/np.sqrt(2)   #TODO: i don't know exactly how the correction should look like!
    super_spatial_constant_3d = 0.66 * constant_scaler
    super_spatial_constant_2d = 0.517 * constant_scaler
    super_spatial_constant_2d_bipartite = super_spatial_constant_2d * bipartite_correction
    super_spatial_constant_3d_bipartite = super_spatial_constant_3d * bipartite_correction
    predicted_medians = [super_spatial_constant_2d, super_spatial_constant_2d_bipartite, super_spatial_constant_3d,
                         super_spatial_constant_3d_bipartite]

    groups = ['2D Non-Bipartite', '2D Bipartite', '3D Non-Bipartite', '3D Bipartite']
    n_class_groups = 4
    # Apply the classification function to each row
    spatial_constant_variation_results_df['classification'] = spatial_constant_variation_results_df.apply(classify_row, axis=1)

    # Step 2: Create the Violin Plot
    plt.figure(figsize=(10, 6))

    # sns.violinplot(x='classification', y='S_general', data=spatial_constant_variation_results_df)
    # Changed it to mean shortest path
    sns.violinplot(x='classification', y=quantity_of_interest, data=spatial_constant_variation_results_df)
    plt.title('Violin Plot Spatial Constant')
    plt.ylabel('Spatial Constant')  # Replace with the name of your variable

    # Plot predictions
    for i in range(n_class_groups):
        plt.scatter(x=i, y=predicted_medians[i], color='red', zorder=3)

    plot_folder = args.directory_map["plots_spatial_constant_variation"]
    plt.savefig(f'{plot_folder}/spatial_constant_variation_violin.png', bbox_inches='tight')







def plot_original_or_reconstructed_image(args, image_type="original", edges_df=None, position_filename=None,
                                         plot_weights_against_distance=False, positions_df=None):
    """Plots the original or reconstructed image based on the provided arguments.

    This function handles the plotting of either the original or reconstructed graph images,
    with options to include weights against distance. It sets up the plot based on the dimensionality
    specified in `args`, retrieves edge data, and plots node positions with optional coloring.

    Args:
        args: An object containing configuration and graph arguments, including directory paths,
              dimensionality (`dim`), color mapping, and more.
        image_type (str): The type of image to plot, options are "original", "mst", or "reconstructed".
                          Defaults to "original".
        edges_df (pandas.DataFrame, optional): DataFrame containing edge data. If None, the edge data
                                               is loaded from a file specified in `args`. Defaults to None.
        position_filename (str, optional): Filename of the position data CSV file. If None, the position
                                           data is loaded based on `image_type` and configurations in `args`.
                                           Defaults to None.
        plot_weights_against_distance (bool): Flag to enable plotting of weights against distance for edges.
                                              Defaults to False.

    Raises:
        ValueError: If `image_type` is not one of the expected options ("original", "reconstructed", "mst").
        ValueError: If the edge list numbering is not valid, indicating a mismatch between edge data and node positions.
    """
    def setup_plot(args, figsize=(10, 8)):
        fig = plt.figure(figsize=figsize)
        if args.dim == 3:
            ax = fig.add_subplot(111, projection='3d')
        elif args.dim == 2:
            ax = fig.add_subplot(111)
        return ax


    def plot_positions(ax, positions_df, args, color_df=None, simulated_colors=False):
        # Merge positions_df with color_df on 'node_ID' if color_df is provided

        if color_df is not None:
            # merged_df = positions_df.merge(color_df, on='node_ID')
            # TODO: this is because shuai colors are incomplete (beacons are missing)

            merged_df = positions_df.merge(color_df, on='node_ID', how='left')
            # merged_df['color'] = merged_df['color'].fillna("gray")

            colors = merged_df['color'].tolist()

            color_priorities = {
                'red': 2,  # Highest priority
                'green': 1,
                'gray': 0,
            }
            priority_list = merged_df['color'].map(color_priorities).tolist()  # Use .fillna(0) to handle any undefined colors with the lowest priority


            if args.dim == 3:
                ax.scatter(merged_df['x'], merged_df['y'], merged_df['z'], color=colors, zorder=priority_list)
            elif args.dim == 2:
                ax.scatter(merged_df['x'], merged_df['y'], color=colors)

        else:
            if simulated_colors:

                if image_type == "reconstructed" and args.node_ids_map_old_to_new is not None:
                    id_to_color = {}
                    for old_index, new_index in args.node_ids_map_old_to_new.items():
                        id_to_color[new_index] = args.id_to_color_simulation[old_index]

                else:
                    id_to_color = args.id_to_color_simulation


                colors = [id_to_color.get(node_id, 'b')  # Default to 'b' if node_id is not in the dictionary
                          for node_id in positions_df['node_ID']]

                if args.dim == 3:
                    ax.scatter(positions_df['x'], positions_df['y'], positions_df['z'],
                               facecolors=colors)
                elif args.dim == 2:
                    ax.scatter(positions_df['x'], positions_df['y'],
                               facecolors=colors)

            else:
                # handle bipartite colors for the case where we do not have a color map
                if args.is_bipartite:
                    color_set1 = '#beaed4'
                    color_set2 = '#fdc086'
                    # Map the bipartite set types to the DataFrame
                    set1 = set(edges_df['source'].unique())
                    set2 = set(edges_df['target'].unique())

                    # Ensure sets are truly disjoint (a requirement for bipartite graphs)
                    set1 = set1 - set2
                    # Map each node to its respective set
                    positions_df['set_label'] = positions_df['node_ID'].apply(
                        lambda x: 'set1' if x in set1 else ('set2' if x in set2 else 'none'))

                    if args.dim == 3:
                        edge_colors = positions_df['set_label'].apply(
                            lambda x: color_set1 if x == 'set1' else color_set2).tolist()
                        ax.scatter(positions_df['x'], positions_df['y'], positions_df['z'], facecolors=edge_colors,
                                   )
                        ax.grid(False)
                        ax.xaxis.pane.fill = False  # Background of the x-axis
                        ax.yaxis.pane.fill = False  # Background of the y-axis
                        ax.zaxis.pane.fill = False  # Background of the z-axis
                        ax.xaxis.pane.set_edgecolor('k')
                        ax.yaxis.pane.set_edgecolor('k')
                        ax.zaxis.pane.set_edgecolor('k')
                        ax.xaxis.pane.set_facecolor('none')
                        ax.yaxis.pane.set_facecolor('none')
                        ax.zaxis.pane.set_facecolor('none')
                    elif args.dim == 2:
                        # Create a color array based on the set label
                        edge_colors = positions_df['set_label'].apply(
                            lambda x: color_set1 if x == 'set1' else color_set2).tolist()
                        ax.scatter(positions_df['x'], positions_df['y'], facecolors=edge_colors, )
                else:  # network is not bipartite, no need to color them differently

                    # if args.dim == 3:
                    #     ax.scatter(positions_df['x'], positions_df['y'], positions_df['z'], facecolors='none',
                    #                edgecolors='b')
                    # elif args.dim == 2:
                    #     ax.scatter(positions_df['x'], positions_df['y'], facecolors='none', edgecolors='b')

                    if args.dim == 3:
                        ax.scatter(positions_df['x'], positions_df['y'], positions_df['z'], facecolors='#7fc97f',
                                   )
                        ax.grid(False)
                        ax.xaxis.pane.fill = False  # Background of the x-axis
                        ax.yaxis.pane.fill = False  # Background of the y-axis
                        ax.zaxis.pane.fill = False  # Background of the z-axis
                        ax.xaxis.pane.set_edgecolor('k')
                        ax.yaxis.pane.set_edgecolor('k')
                        ax.zaxis.pane.set_edgecolor('k')
                        ax.xaxis.pane.set_facecolor('none')
                        ax.yaxis.pane.set_facecolor('none')
                        ax.zaxis.pane.set_facecolor('none')
                    elif args.dim == 2:
                        ax.scatter(positions_df['x'], positions_df['y'], facecolors='#7fc97f', )

        if args.dim == 3:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])

        elif args.dim == 2:
            # Hide axes ticks
            ax.set_xticks([])
            ax.set_yticks([])

            # Hide the axes
            ax.axis('off')

    # image_type: original, mst, reconstructed


    # Simulated colors should only be used for simulation proximity modes
    if args.colorfile is not None:
        if args.colorfile[-4:] != '.csv' and args.proximity_mode == "experimental":
            args.colorfile = None


    # TODO: this should not be working when we reconstruct with sparse matrices right? The order of the edge list is different (so positions and graph are different)
    if edges_df is None:
        edge_list_folder = args.directory_map["edge_lists"]
        edges_df = pd.read_csv(f"{edge_list_folder}/{args.edge_list_title}")
        if args.verbose:
            print(f"retrieving edges from {args.edge_list_title}")

    # Get the positions
    if image_type == "original" or image_type == "mst":

        if positions_df is None:
            original_position_folder = args.directory_map["original_positions"]
            if position_filename is None:
                positions_df = pd.read_csv(f"{original_position_folder}/positions_{args.original_title}.csv")
                # positions_df = pd.read_csv(f"{original_position_folder}/positions_{args.args_title}.csv")
            else:
                positions_df = pd.read_csv(f"{original_position_folder}/{position_filename}")


        if args.colorfile is not None:
            # Check if the colorfile is an image
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']
            colorfile_extension = os.path.splitext(args.colorfile)[1].lower()
            if colorfile_extension in image_extensions:
                args.id_to_color_simulation = map_points_to_colors(positions_df, args.colorfile, args=args)

    elif image_type == "reconstructed":
        edge_list_folder = args.directory_map["edge_lists"]
        edges_df = pd.read_csv(f"{edge_list_folder}/{args.edge_list_title}")
        reconstructed_position_folder = args.directory_map["reconstructed_positions"]
        if position_filename is None:
            positions_df = pd.read_csv(f"{reconstructed_position_folder}/positions_{args.args_title}.csv")
        else:
            positions_df = pd.read_csv(f"{reconstructed_position_folder}/{position_filename}")

        if args.colorfile is not None:
            if args.proximity_mode != "experimental":
                original_position_folder = args.directory_map["original_positions"]
                original_positions_df = pd.read_csv(f"{original_position_folder}/positions_{args.original_title}.csv")
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']
                colorfile_extension = os.path.splitext(args.colorfile)[1].lower()
                if colorfile_extension in image_extensions:
                    args.id_to_color_simulation = map_points_to_colors(original_positions_df, args.colorfile, args=args)

        is_valid, reason = validate_edge_list_numbers(edges_df, np.array(positions_df))
        if not is_valid:
            print("Reason edge list is not valid:", reason)
            raise ValueError("Edge list numbering is not valid! It should go from 0 to N-1 points")
    else:
        raise ValueError("Please specify a correct value for image_type, either original or reconstructed.")

    ax = setup_plot(args)


    # Plot data
    if (args.colorfile is not None) and args.proximity_mode == "experimental":
        # Change the position ID for weinstein case also
        if args.colorfile[:4] == "wein" and image_type == 'original':  # mapping should only be applied when we have original image
            if args.node_ids_map_old_to_new is not None:
                positions_df['node_ID'] = positions_df['node_ID'].map(args.node_ids_map_old_to_new)
                positions_df = positions_df.dropna()
                positions_df['node_ID'] = positions_df['node_ID'].astype(int)

        ### Plot from color ID file
        color_folder = args.directory_map["colorfolder"]
        print(f"{color_folder}/{args.colorfile}")
        color_df = pd.read_csv(f"{color_folder}/{args.colorfile}")


        color_df['color'] = color_df['color'].map(args.colorcode)
        # If we selected a largest component then we need to map the node ids to the proper color
        if args.node_ids_map_old_to_new is not None:
            color_df['node_ID'] = color_df['node_ID'].map(args.node_ids_map_old_to_new)
            color_df = color_df.dropna()


        # Additional processing for color_df if required
        plot_positions(ax, positions_df, args, color_df)
    else:
        if args.id_to_color_simulation is not None:
            plot_positions(ax, positions_df, args, simulated_colors=True)
        else:
            plot_positions(ax, positions_df, args)

        # TODO: check that this makes sense for every case where we have old and new indices
        ## This applies the new mapping so the (new) edges get the right positions
        if args.node_ids_map_old_to_new is not None and image_type == 'original':
            positions_df['node_ID'] = positions_df['node_ID'].map(args.node_ids_map_old_to_new)
            positions_df = positions_df.dropna()
            positions_df['node_ID'] = positions_df['node_ID'].astype(int)

    if plot_weights_against_distance:
        distances = []
        weights = []

    number_of_edges = edges_df.shape[0]
    if args.verbose:
        print("NUMBER OF EDGES", number_of_edges)

    if number_of_edges > 100000:
        warnings.warn("Too many edges (>100000), skip plotting them")
    else:
        # Draw edges
        for _, row in edges_df.iterrows():
            filtered_df = positions_df[positions_df['node_ID'] == row['source']]
            if not filtered_df.empty:
                source = filtered_df.iloc[0]
            else:
                continue

            source = positions_df[positions_df['node_ID'] == row['source']].iloc[0]     # TODO: is this the most efficient?
            target = positions_df[positions_df['node_ID'] == row['target']].iloc[0]

            edge_color = 'red' if (row['source'], row['target']) in args.false_edge_ids or (
            row['target'], row['source']) in args.false_edge_ids else 'k'

            edge_alpha = 1 if (row['source'], row['target']) in args.false_edge_ids or (
            row['target'], row['source']) in args.false_edge_ids else 0.8    # edge opacity

            edge_linewidth = 5 if (row['source'], row['target']) in args.false_edge_ids or (  #TODO: adjust linewidth
            row['target'], row['source']) in args.false_edge_ids else 0.5

            if args.dim == 3:
                ax.plot([source['x'], target['x']], [source['y'], target['y']], [source['z'], target['z']],
                        edge_color, linewidth=edge_linewidth, alpha=edge_alpha)
            else:
                ax.plot([source['x'], target['x']], [source['y'], target['y']],
                        edge_color, linewidth=edge_linewidth, alpha=edge_alpha)

            if plot_weights_against_distance:
                distance = np.sqrt((source['x'] - target['x']) ** 2 + (source['y'] - target['y']) ** 2)
                distances.append(distance)
                weights.append(row['weight'])



    if "pbmc" in args.edge_list_title:
        format_extension = '.svg'
    else:
        format_extension = '.svg' if args.num_points < 1000 else '.png'
    if image_type == "original":
        plot_folder = args.directory_map["plots_original_image"]
        plt.savefig(f"{plot_folder}/original_image_{args.args_title}_{args.point_mode}{format_extension}")

        plot_folder2 = args.directory_map['spatial_coherence']
        plt.savefig(f"{plot_folder2}/original_image_{args.args_title}_{args.point_mode}{format_extension}")
        # plt.savefig(f"{plot_folder}/original_image_{args.args_title}", format='svg')
        write_network_in_json_format(positions_df=positions_df, args=args, edges_df=edges_df, network_type='original')
    elif image_type == "mst":
        plot_folder = args.directory_map["plots_mst_image"]
        plt.savefig(f"{plot_folder}/mst_image_{args.args_title}{format_extension}")
        # plt.savefig(f"{plot_folder}/mst_image_{args.args_title}", format='svg')
        plot_folder2 = args.directory_map['spatial_coherence']
        plt.savefig(f"{plot_folder2}/mst_image_{args.args_title}{format_extension}")
    else:
        plot_folder = args.directory_map["plots_reconstructed_image"]
        plot_folder2 = args.directory_map['spatial_coherence']
        plot_folder3 = args.directory_map['rec_images_subgraphs']
        plt.savefig(f"{plot_folder}/reconstructed_image_{args.args_title}_{args.point_mode}{format_extension}")
        plt.savefig(f"{plot_folder2}/reconstructed_image_{args.args_title}_{args.point_mode}{format_extension}")
        plt.savefig(f"{plot_folder3}/reconstructed_image_{args.args_title}_{args.point_mode}{format_extension}")
        # plt.savefig(f"{plot_folder}/reconstructed_image_{args.args_title}", format='svg')

        write_network_in_json_format(positions_df=positions_df, args=args, edges_df=edges_df,
                                     network_type='reconstructed')


    if plot_weights_against_distance:
        #### Create new dataframe
        # Merge edges with positions for source nodes
        merged_df = edges_df.merge(positions_df, how='left', left_on='source', right_on='node_ID',
                                   suffixes=('', '_source'))
        merged_df.rename(columns={'x': 'x_source', 'y': 'y_source', 'z': 'z_source'}, inplace=True)

        # Merge edges with positions for target nodes
        merged_df = merged_df.merge(positions_df, how='left', left_on='target', right_on='node_ID',
                                    suffixes=('', '_target'))
        merged_df.rename(columns={'x': 'x_target', 'y': 'y_target', 'z': 'z_target'}, inplace=True)

        # Calculate Euclidean distance
        if 'z_source' in merged_df.columns:  # Check if 3D data is available
            merged_df['distance'] = np.sqrt(
                (merged_df['x_source'] - merged_df['x_target']) ** 2 +
                (merged_df['y_source'] - merged_df['y_target']) ** 2 +
                (merged_df['z_source'] - merged_df['z_target']) ** 2
            )
        else:  # For 2D data
            merged_df['distance'] = np.sqrt(
                (merged_df['x_source'] - merged_df['x_target']) ** 2 +
                (merged_df['y_source'] - merged_df['y_target']) ** 2
            )

        # Create the improved edge list
        improved_edge_list = merged_df[['source', 'target', 'weight', 'distance']]
        plot_folder = args.directory_map["plots_original_image"]
        improved_edge_list.to_csv(f'{plot_folder}/improved_edge_list_{args.args_title}.csv', index=False)

        print("esta passant...")
        plt.figure(figsize=(10, 6))
        plt.scatter(distances, weights, color='blue', edgecolor='k')
        plt.title('Euclidean Distance vs. Weight')
        plt.xlabel('Euclidean Distance')
        plt.ylabel('Weight')
        plt.savefig(f"{plot_folder}/weight_distance_{args.args_title}_linear")
        plt.yscale('log')
        plt.xscale('log')
        plt.savefig(f"{plot_folder}/weight_distance_{args.args_title}_log")

        from scipy.stats import gaussian_kde
        # Logarithmic transformation with a small shift to handle zero weights
        log_weights = np.log10(np.array(weights) + 1)
        log_distances = np.log10(np.array(distances) + 1)

        # Calculate the point density
        xy = np.vstack([log_distances, log_weights])
        z = gaussian_kde(xy)(xy)
        fig, ax = plt.subplots(figsize=(10, 6))
        sc = ax.scatter(log_distances, log_weights, c=z, s=50, edgecolor='none', cmap='viridis')
        fig.colorbar(sc, ax=ax, label='Density')

        ax.set_title('Log-Transformed Weights vs. Distances with Density Coloring')
        ax.set_xlabel('Log of Euclidean Distance')
        ax.set_ylabel('Log of Weight')
        plt.savefig(f"{plot_folder}/weight_distance_{args.args_title}_log_with_density")


        # ### Boxplot
        # bins = np.linspace(min(distances), max(distances), num=10)  # Adjust num for more or fewer bins
        # binned_distances = np.digitize(distances, bins)
        #
        # fig, ax = plt.subplots(figsize=(10, 6))
        # for i in range(1, len(bins)):
        #     data = [weights[binned_distances == j] for j in range(1, len(bins))]
        #     ax.boxplot(data, positions=[(bins[j - 1] + bins[j]) / 2 for j in range(1, len(bins))],
        #                widths=np.diff(bins) * 0.6)
        #
        # ax.set_title('Binned Euclidean Distance vs. Weight')
        # ax.set_xlabel('Euclidean Distance')
        # ax.set_ylabel('Weight')
        # plt.xticks(ticks=bins, labels=[f"{bins[i]:.2f}" for i in range(len(bins))], rotation=45)
        # plt.savefig(f"{plot_folder}/binned_weight_distance_boxplot.png")
    if args.show_plots:
        plt.show()
    plt.close('all')

def plot_shortest_path_heatmap(args, shortest_path_matrix, ax, vmin, vmax, positions_df=None,
                               edges_df=None, n_false_edges=0):
    original_position_folder = args.directory_map["original_positions"]
    if positions_df is None:
        positions_df = pd.read_csv(f"{original_position_folder}/positions_{args.original_title}.csv")

    if edges_df is None:
        edge_list_folder = args.directory_map["edge_lists"]
        edges_df = pd.read_csv(f"{edge_list_folder}/{args.edge_list_title}")
        if args.verbose:
            print(f"retrieving edges from {args.edge_list_title}")

    central_node_ID = find_geometric_central_node(positions_df=positions_df)
    node_ID_to_shortest_path_mapping = (
        compute_shortest_path_mapping_from_central_node(central_node_ID=central_node_ID, positions_df=positions_df,
                                                    shortest_path_matrix=shortest_path_matrix))

    distances_df = pd.DataFrame(list(node_ID_to_shortest_path_mapping.items()), columns=['node_ID', 'distance'])
    merged_df = pd.merge(positions_df, distances_df, on='node_ID')
    partition_int = np.ceil(np.sqrt(args.num_points))
    grid_x, grid_y = np.mgrid[min(merged_df.x):max(merged_df.x):complex(0, partition_int),
                     min(merged_df.y):max(merged_df.y):complex(0, partition_int)]
    grid_z = griddata((merged_df.x, merged_df.y), merged_df.distance, (grid_x, grid_y), method='cubic')


    # Use ax (the subplot axes) for plotting instead of plt directly
    image = ax.imshow(grid_z.T, extent=(min(merged_df.x), max(merged_df.x), min(merged_df.y), max(merged_df.y)),
                      origin='lower', aspect='auto', cmap='viridis', vmin=vmin, vmax=vmax)

    positions_indexed = positions_df.set_index('node_ID')
    if args.false_edge_ids and edges_df is not None:
        for edge in args.false_edge_ids[:n_false_edges]:
            # Extract source and target from the tuple, handling both directions
            source, target = edge
            # Ensure the edge exists in the DataFrame
            if (source in positions_indexed.index) and (target in positions_indexed.index):
                source_pos = positions_indexed.loc[source]
                target_pos = positions_indexed.loc[target]
                ax.plot([source_pos.x, target_pos.x], [source_pos.y, target_pos.y], color='red', linewidth=0.5, alpha=0.3)

    # Optionally set titles, labels, etc., using the ax object
    ax.set_title(f'False Edges {n_false_edges}')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    # Return the image object for potential use with colorbars, etc.
    return image

    # # Plotting
    # plt.figure(figsize=(10, 8))
    # plt.imshow(grid_z.T, extent=(min(merged_df.x), max(merged_df.x), min(merged_df.y), max(merged_df.y)),
    #            origin='lower')
    # plt.colorbar(label='Shortest path distance to central node')
    #
    # plt.xlabel('X ')
    # plt.ylabel('Y ')
    # plt.grid(False)
    #
    # plot_folder = args.directory_map['plots_shortest_path_heatmap']
    # plt.savefig(f'{plot_folder}_heatmap_sp_{args.args_title}')
    # plt.show()

def compute_grid_z(args, shortest_path_matrix, positions_df=None):
    if positions_df is None:
        original_position_folder = args.directory_map["original_positions"]
        positions_df = pd.read_csv(f"{original_position_folder}/positions_{args.original_title}.csv")

    central_node_ID = find_geometric_central_node(positions_df=positions_df)
    node_ID_to_shortest_path_mapping = compute_shortest_path_mapping_from_central_node(
        central_node_ID=central_node_ID, positions_df=positions_df, shortest_path_matrix=shortest_path_matrix
    )

    distances_df = pd.DataFrame(list(node_ID_to_shortest_path_mapping.items()), columns=['node_ID', 'distance'])
    merged_df = pd.merge(positions_df, distances_df, on='node_ID')
    partition_int = np.ceil(np.sqrt(args.num_points))  # Adjust partition based on number of points
    grid_x, grid_y = np.mgrid[min(merged_df.x):max(merged_df.x):complex(0, partition_int),
                              min(merged_df.y):max(merged_df.y):complex(0, partition_int)]
    grid_z = griddata((merged_df.x, merged_df.y), merged_df.distance, (grid_x, grid_y), method='cubic')

    return grid_z

def plot_multiple_shortest_path_heatmaps(args, sp_matrices, false_edge_list):
    # Create a figure for the subplots
    num_plots = len(sp_matrices)
    fig, axs = plt.subplots(1, num_plots, figsize=(20, 5), constrained_layout=True)

    # vmin = np.min(sp_matrices[0])
    # vmax = np.max(sp_matrices[0])
    # for matrix in sp_matrices:
    #     vmin = min(vmin, np.min(matrix))
    #     vmax = max(vmax, np.max(matrix))

    all_grid_z = [compute_grid_z(args, sp_matrix) for sp_matrix in sp_matrices]

    vmin = np.min([np.nanmin(grid) for grid in all_grid_z])
    vmax = np.max([np.nanmax(grid) for grid in all_grid_z])


    # Now plot each with consistent color scale
    for i, sp_matrix in enumerate(sp_matrices):
        # Assuming plot_shortest_path_heatmap can accept subplot axes and color limits
        n_false_edges = false_edge_list[i]
        plot_shortest_path_heatmap(args, shortest_path_matrix=sp_matrix, ax=axs[i], vmin=vmin, vmax=vmax, n_false_edges=n_false_edges)

    # Create a single colorbar for the whole figure
    fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax), cmap="viridis"), ax=axs,
                 orientation='horizontal', fraction=0.02, pad=0.04, label="Shortest Path Distance")
    plot_folder = args.directory_map['plots_shortest_path_heatmap']
    plt.savefig(f'{plot_folder}/heatmap_several_sp_matrix{args.args_title}.png')
    plt.savefig(f'{plot_folder}/heatmap_several_sp_matrix{args.args_title}.svg')
    if args.show_plots:
        plt.show()
    plt.close()



def calculate_predicted_s(args):
    ### Predictions
    constant_scaler = np.sqrt(4.5)
    bipartite_correction = 1 / 1.2  # 1/np.sqrt(2)   #TODO: i don't know exactly how the correction should look like!
    super_spatial_constant_3d = 0.66 * constant_scaler
    super_spatial_constant_2d = 0.517 * constant_scaler
    super_spatial_constant_2d_bipartite = super_spatial_constant_2d * bipartite_correction
    super_spatial_constant_3d_bipartite = super_spatial_constant_3d * bipartite_correction

    if args.dim == 2:
        if args.is_bipartite:
            return super_spatial_constant_2d_bipartite  # Replace with actual calculation
        else:
            return super_spatial_constant_2d  # Replace with actual calculation
    elif args.dim == 3:
        if args.is_bipartite:
            return super_spatial_constant_3d_bipartite  # Replace with actual calculation
        else:
            return super_spatial_constant_3d  # Replace with actual calculation

def plot_sample_spatial_constant(args, dataframe):

    unique_sizes = dataframe['intended_size'].unique()
    plt.figure(figsize=(10, 6))

    # Determine the global range for all histograms
    min_value = dataframe['S_general'].min()
    max_value = dataframe['S_general'].max()
    bin_edges = np.linspace(min_value, max_value, 21)  # 20 bins across the full range

    for size in unique_sizes:
        subset = dataframe[dataframe['intended_size'] == size]
        plt.hist(subset['S_general'], alpha=0.5, label=f'Size {size}', bins=bin_edges)

    predicted_s = calculate_predicted_s(args=args)
    plt.axvline(predicted_s, color='r', linestyle='dashed', linewidth=2, label='Predicted S')

    plt.xlabel('S_general')
    plt.ylabel('Frequency')
    plt.title('Histogram of S_general for each Intended Size')
    plt.legend()

    plot_folder = f"{args.directory_map['plots_spatial_constant_subgraph_sampling']}"
    plt.savefig(f"{plot_folder}/subgraph_sampling_{args.args_title}")
    if args.show_plots:
        plt.show()
    plt.close()


def plot_spatial_constant_against_subgraph_size(args, dataframe, use_depth=False):

    if use_depth:
        size_magnitude = 'depth'
        s_constant = 'S_depth'
    else:
        size_magnitude = 'intended_size'
        s_constant = 'S_general'


    unique_sizes = dataframe[size_magnitude].unique()
    means = []
    std_devs = []
    sizes = []

    # Calculate mean and standard deviation for each size
    for size in unique_sizes:
        subset = dataframe[dataframe[size_magnitude] == size]
        mean = subset[s_constant].mean()
        std = subset[s_constant].std()
        means.append(mean)
        std_devs.append(std)
        sizes.append(size)

    plt.figure(figsize=(10, 6))

    sizes = np.array(sizes)
    means = np.array(means)
    std_devs = np.array(std_devs)


    plt.plot(sizes, means, color='#00CD6C', marker='o')
    plt.fill_between(sizes, means - std_devs, means + std_devs, color='#00CD6C', alpha=0.3)




    # # Optionally, plot the predicted S line if needed
    # predicted_s = calculate_predicted_s(args=args)
    # plt.axhline(predicted_s, color='r', linestyle='dashed', linewidth=2, label='Predicted S')

    if use_depth:
        plt.xlabel('Depth')
    else:
        plt.xlabel('Size')
    plt.ylabel('Mean Spatial Constant')

    plt.legend()

    plot_folder = f"{args.directory_map['plots_spatial_constant_subgraph_sampling']}"
    plot_folder2 = f"{args.directory_map['spatial_coherence']}"
    plt.savefig(f"{plot_folder}/mean_s_general_vs_{size_magnitude}_{args.args_title}.png")
    plt.savefig(f"{plot_folder2}/mean_s_general_vs_{size_magnitude}_{args.args_title}.{args.format_plots}")
    # if args.show_plots:
    #     plt.show()
    plt.close()



def plot_spatial_constant_against_subgraph_size_with_false_edges(args, dataframes, false_edge_list, mst_case_df=None,
                                                                 use_depth=False):
    plt.close('all')
    # Main plot spatial constant
    plt.figure(figsize=(6, 4.5))

    if use_depth:
        size_magnitude = 'depth'
        # s_constant = 'S_depth'
        s_constant = 'S_general'
    else:
        size_magnitude = 'intended_size'
        s_constant = 'S_general'


    for dataframe, false_edge_count in zip(dataframes, false_edge_list):
        unique_sizes = dataframe[size_magnitude].unique()
        means = []
        std_devs = []
        sizes = []

        # Calculate mean and standard deviation for each size
        for size in unique_sizes:
            subset = dataframe[dataframe[size_magnitude] == size]
            mean = subset[s_constant].mean()
            std = subset[s_constant].std()
            means.append(mean)
            std_devs.append(std)
            sizes.append(size)

        sizes = np.array(sizes)
        means = np.array(means)
        std_devs = np.array(std_devs)


        # Plot each series
        label = f'False Edges: {false_edge_count}'
        plt.plot(sizes, means, label=label, marker='o')
        plt.fill_between(sizes, means - std_devs, means + std_devs, alpha=0.3)



    if mst_case_df is not None:
        unique_sizes = mst_case_df['intended_size'].unique()
        means = [mst_case_df[mst_case_df['intended_size'] == size]['S_general'].mean() for size in unique_sizes]
        std_devs = [mst_case_df[mst_case_df['intended_size'] == size]['S_general'].std() for size in unique_sizes]

        plt.plot(unique_sizes, means, label='MST', marker='o')
        plt.fill_between(unique_sizes, np.array(means) - np.array(std_devs), np.array(means) + np.array(std_devs), alpha=0.3)

    if use_depth:
        plt.xlabel('Depth')
    else:
        plt.xlabel('Size')


    plt.ylabel('Mean Spatial Constant')
    # plt.title('Mean Spatial Constant vs. Size')
    plt.legend()

    plot_folder = args.directory_map['plots_spatial_constant_subgraph_sampling']
    plot_folder2 = args.directory_map['spatial_coherence']

    plt.savefig(f"{plot_folder}/mean_s_general_vs_{size_magnitude}_{args.args_title}_false_edge_version.svg")
    plt.savefig(f"{plot_folder2}/mean_s_general_vs_{size_magnitude}_{args.args_title}_false_edge_version.{args.format_plots}")


    if args.show_plots:
        plt.show()
    plt.close()

    plt.yscale('log')
    plt.savefig(f"{plot_folder}/mean_s_general_vs_{size_magnitude}_{args.args_title}_false_edge_loglin_version.png")
    plt.close('all')

    plt.xscale('log')
    plt.yscale('log')
    plt.savefig(f"{plot_folder}/mean_s_general_vs_{size_magnitude}_{args.args_title}_false_edge_loglog_version.png")
    plt.close('all')


def plot_spatial_constant_against_subgraph_size_with_multiple_series(args, dataframe, false_edge_counts, ax=None, title=None, mst_case_df=None):
    # Use provided axis or get/create current active axis
    if ax is None:
        ax = plt.gca()


    # Unique values in the 'proximity_mode' column
    proximity_modes = dataframe['proximity_mode'].unique()

    # Loop through each proximity mode
    for mode in proximity_modes:
        # Extract the number of false edges from the proximity mode string
        match = re.search(r'with_false_edges=(\d+)', mode)
        false_edge_count = int(match.group(1)) if match else 0

        # Filter the DataFrame for the current proximity mode
        filtered_df = dataframe[dataframe['proximity_mode'] == mode]
        unique_sizes = filtered_df['intended_size'].unique()
        means = []
        std_devs = []
        sizes = []

        # Calculate mean and standard deviation for each size
        for size in unique_sizes:
            subset = filtered_df[filtered_df['intended_size'] == size]
            mean = subset['S_general'].mean()
            std = subset['S_general'].std()
            means.append(mean)
            std_devs.append(std)
            sizes.append(size)

        sizes = np.array(sizes)
        means = np.array(means)
        std_devs = np.array(std_devs)

        # Plot each series on the given axis
        label = f'False Edges: {false_edge_count}'
        ax.plot(sizes, means, label=label, marker='o')
        ax.fill_between(sizes, means - std_devs, means + std_devs, alpha=0.3)


    if mst_case_df is not None:
        pass

    ax.set_xlabel('Size')
    ax.set_ylabel('Mean Spatial Constant')
    if title:
        ax.set_title(title)
    ax.legend()

    # Save plot if ax is not provided (assumed to be a standalone plot)
    if ax is None:
        plot_folder = args.directory_map['plots_spatial_constant_subgraph_sampling']
        plt.savefig(f"{plot_folder}/mean_s_general_vs_intended_size_{args.args_title}_false_edge_version.png")


def plot_spatial_constants_subplots(args, all_dataframes, all_false_edge_lists, weight_thresholds, mst_case_df=None):
    num_plots = len(weight_thresholds)
    fig, axs = plt.subplots(1, num_plots, figsize=(10 * num_plots, 6), sharey=True)

    # Ensure axs is iterable when there's only one subplot
    if num_plots == 1:
        axs = [axs]

    for idx, wt in enumerate(weight_thresholds):
        # Extract the DataFrames and false_edge_counts for the current weight threshold
        dataframes_for_wt = all_dataframes[idx]
        false_edge_counts_for_wt = all_false_edge_lists[idx]

        # Call the modified plot function for each subplot
        plot_spatial_constant_against_subgraph_size_with_multiple_series(
            args, dataframes_for_wt, false_edge_counts_for_wt, ax=axs[idx], title=f"Weight Threshold: {wt}", mst_case_df=mst_case_df
        )

    plt.tight_layout()
    plot_folder = args.directory_map['plots_spatial_constant_subgraph_sampling']
    plt.savefig(f"{plot_folder}/spatial_constant_subgraphs_different_weight_threshold_{args.args_title}_false_edge_version.png")
    plt.savefig(
        f"{plot_folder}/spatial_constant_subgraphs_different_weight_threshold_{args.args_title}_false_edge_version.{args.format_plots}")

def plot_false_edges_against_spatial_constant(args, processed_false_edge_series):
    plot_folder = args.directory_map['plots_spatial_constant_false_edge_difference']

    # Determine the unique intended_subgraph_sizes across all dataframes
    all_sizes = set(list(processed_false_edge_series.keys()))


    # Create a single plot
    fig1, ax1 = plt.subplots(figsize=(10, 6))

    cmap_name = 'Oranges_d'
    colors = sns.color_palette(cmap_name, len(all_sizes))
    # colors = cm.get_cmap('magma_r', len(all_sizes))
    cmap = sns.color_palette(cmap_name, as_cmap=True)
    # Normalizing the size values for the color mapping
    norm = mcolors.Normalize(vmin=min(all_sizes), vmax=max(all_sizes))

    # Exctract each series and plot
    for i, size in enumerate(sorted(all_sizes)):
        plot_folder_fit = args.directory_map['plots_spatial_constant_false_edge_difference_fits']
        false_edges = processed_false_edge_series[size]["false_edges"]
        means = processed_false_edge_series[size]["means"]  # Spatial Constant means
        std_devs = processed_false_edge_series[size]["std_devs"]

        # Plotting the series for the current Size
        ax1.errorbar(false_edges, means, yerr=std_devs, color=colors[i], label=f'Size: {size}', marker='o')
        # plt.errorbar(false_edges, means, yerr=std_devs, color=colors(i), label=f'Size: {size}', marker='o')  # for matplotlib

        log_false_edges = np.log(np.array(false_edges) + 1)  # +1 to avoid zero error
        log_means = np.log(means)
        curve_fitting_object = CurveFitting(log_false_edges, log_means)
        func_fit = curve_fitting_object.linear_model
        curve_fitting_object.perform_curve_fitting(model_func=func_fit)
        save_path = f"{plot_folder_fit}/false_edge_powerlaw_fit_size={size}_{args.args_title}_fedgelist={false_edges}.{args.format_plots}"
        curve_fitting_object.plot_fit_with_uncertainty(model_func=func_fit, xlabel="Log False Edge Count",
                                                       ylabel="Log Spatial Constant", title=f"Size {size}", save_path=save_path)

    ax1.set_title('Spatial Constant vs False Edge Count')
    ax1.set_xlabel('False Edge Count')
    ax1.set_ylabel('Spatial Constant')

    # Creating a colorbar for the sizes
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax1)
    cbar.set_label('Size')

    # plt.legend(loc='upper left', bbox_to_anchor=(1, 1))


    fig1.tight_layout()
    fig1.savefig(f"{plot_folder}/normal_false_edge_difference_{args.args_title}_fedgelist={false_edges}.{args.format_plots}")

    ax1.set_xscale('log')
    fig1.savefig(f"{plot_folder}/semilogX_false_edge_difference_{args.args_title}_fedgelist={false_edges}.{args.format_plots}")

    ax1.set_yscale('log')
    ax1.set_xscale('linear')
    fig1.savefig(f"{plot_folder}/semilogY_false_edge_difference_{args.args_title}_fedgelist={false_edges}.{args.format_plots}")

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    fig1.savefig(f"{plot_folder}/loglog_false_edge_difference_{args.args_title}_fedgelist={false_edges}.{args.format_plots}")

def plot_weight_distribution(args, edge_list_with_weight_df):
    # # Histogram Plot
    # plt.figure(figsize=(12, 6))
    # plt.subplot(1, 2, 1)  # 1 row, 2 columns, first subplot
    # plt.hist(edge_list_with_weight_df['weight'], bins=20, color='skyblue', edgecolor='black', log=True)
    # plt.title('Histogram of Weights')
    # plt.xscale('log')
    # plt.xlabel('Weight')
    # plt.ylabel('Frequency')

    unique_weights = edge_list_with_weight_df['weight'].unique()
    num_unique_weights = len(unique_weights)
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)  # 1 row, 2 columns, first subplot
    plt.hist(edge_list_with_weight_df['weight'], bins=num_unique_weights, color='skyblue', edgecolor='black', log=True)
    plt.title('Histogram of Weights')
    plt.xlabel('Weight')
    plt.ylabel('Frequency')


    # Prepare DataFrame for Scatter Plot - Ordered by weight
    sorted_df = edge_list_with_weight_df.sort_values(by='weight')
    sorted_df['rank'] = range(1, len(sorted_df) + 1)

    # Scatter Plot - Ordered by weight
    plt.subplot(1, 2, 2)  # 1 row, 2 columns, second subplot
    plt.scatter(sorted_df['rank'], sorted_df['weight'], color='tomato')
    plt.title('Scatter Plot of Weights (Ordered by Rank)')
    plt.xlabel('Rank')
    plt.ylabel('Weight')


    # Show plots
    plt.tight_layout()
    plot_folder = args.directory_map['plots_weight_distribution']
    plt.savefig(f"{plot_folder}/weight_distribution_{args.args_title}.png")
    if args.show_plots:
        plt.show()
    plt.close()


def plot_s_general_vs_weight_threshold(args, results):

    weight_thresholds, s_generals = zip(*results)

    # Scatter Plot
    plt.figure(figsize=(10, 6))
    plt.plot(weight_thresholds, s_generals, marker='o', color='blue', linestyle='-', linewidth=2, markersize=8)
    plt.title('Mean S_general vs. Weight Threshold')
    plt.xlabel('Weight Threshold')
    plt.ylabel('Mean S_general')
    plot_folder = args.directory_map['plots_spatial_constant_weighted_threshold']
    plt.savefig(f"{plot_folder}/spatial_constant_vs_weight_threshold{args.args_title}.png")
    plt.savefig(f"{plot_folder}/spatial_constant_vs_weight_threshold{args.args_title}.{args.format_plots}")

def validate_edge_list_numbers(edge_list, reconstructed_positions):
    n = len(reconstructed_positions) - 1
    expected_set = set(range(n + 1))

    # Create a set of all values in 'source' and 'target'
    edge_values = set(edge_list['source']).union(set(edge_list['target']))

    if edge_values == expected_set:
        return True, "Edge list is valid."

    missing = expected_set - edge_values
    extra = edge_values - expected_set

    mismatch_info = []
    if missing:
        mismatch_info.append(f"Missing nodes: {missing}")
    if extra:
        mismatch_info.append(f"Extra nodes: {extra}")

    return False, "; ".join(mismatch_info)

    return edge_values == expected_set


def save_plotting_data(column_names, data, csv_filename,):
    """
    Saves plotting data to a CSV file and optionally creates a basic plot.

    Parameters:
    - column_names: List of column names.
    - data: List of data arrays, where each array corresponds to a column.
    - csv_filename: Filename for the output CSV file.
    - plot_filename: Optional filename for saving the plot. If None, no plot is saved.
    """

    data_float = []
    for arr in data:
        if isinstance(arr, list):  # Check if the data is in list format
            arr = np.array(arr)   # Convert list to NumPy array
        if arr.dtype.kind in 'ui':  # Check if the array is of integer type
            arr = arr.astype(float)  # Convert integer array to float
        data_float.append(arr)
    max_length = max(len(arr) for arr in data_float)
    padded_data = [np.pad(arr, (0, max_length - len(arr)), 'constant', constant_values=np.nan) for arr in data_float]
    df = pd.DataFrame({col: dat for col, dat in zip(column_names, padded_data)})
    df.to_csv(csv_filename, index=False)
    print(f'Data saved to {csv_filename}')

def write_network_in_json_format(args, positions_df, edges_df, network_type):
    # Determine if the positions are in 2D or 3D
    if 'z' in positions_df.columns:
        node_fields = ['node_ID', 'x', 'y', 'z']
    else:
        positions_df['z'] = 0  # Add a 'z' column with 0 values if it is a 2D DataFrame
        node_fields = ['node_ID', 'x', 'y', 'z']


    # Calculate distances
    coordinates = positions_df[['x', 'y', 'z']].to_numpy()
    distances = pdist(coordinates)  # Compute the pairwise distances between rows
    median_distance = np.median(distances)

    # Determine scale factor and val based on the median distance
    scale_factor = 100 / median_distance
    val = 0.01

    # Apply scaling
    positions_df['x'] *= scale_factor
    positions_df['y'] *= scale_factor
    positions_df['z'] *= scale_factor
    positions_df['val'] = val
    positions_df['name'] = positions_df['node_ID']

    # Validate the positions DataFrame
    for field in node_fields:
        if field not in positions_df.columns:
            raise ValueError(f"Missing required field in positions DataFrame: {field}")

    # Validate the edges DataFrame
    if 'source' not in edges_df.columns or 'target' not in edges_df.columns:
        raise ValueError("Edges DataFrame must contain 'source' and 'target' columns")

    # Convert positions DataFrame to the nodes list
    nodes = positions_df.rename(columns={'node_ID': 'id'}).to_dict(orient='records')

    # Convert edges DataFrame to the links list
    links = edges_df.to_dict(orient='records')

    for link in links:
        if (link['source'], link['target']) in args.false_edge_ids or (link['target'], link['source']) in args.false_edge_ids:
            link['color'] = '#ff0000'
            link['width'] = 2.5

    # Create the graph dictionary
    graph_data = {
        "nodes": nodes,
        "links": links
    }

    # Construct the file path
    data_folder = args.directory_map["json"]
    file_path = f'{data_folder}/json_format_{network_type}_{args.args_title}.json'
    # Write the graph dictionary to a JSON file
    with open(file_path, 'w') as f:
        json.dump(graph_data, f, indent=4)
    # print(f"Graph JSON file saved to {file_path}")