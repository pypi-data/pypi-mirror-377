# Base settings common to all scenarios
base = {
    "proximity_mode": "delaunay_corrected",  # Options 1) Simulation: knn, knn_bipartite,  epsilon-ball, epsilon_bipartite, lattice, delaunay_corrected, distance_decay... 2) experimental
    "dim": 2,
    "false_edges_count": 0,
    "true_edges_deletion_ratio": 0,
    "colorfile": None,  # For coloring reconstruction. Alternatives: colorful_spiral.jpeg, colored_squares.png, dna.jpg, dna_cool2.png, color_gradient.jpg, weinstein_colorcode_february_corrected.csv, None
    "plot_graph_properties": False,
    "show_plots": True,
    "format_plots": 'svg',  #pdf, png...
    "write_json_format": False,
    "precompute_shortest_paths": False,

    "large_graph_subsampling": False,   # If the graph is large, subsample it to save time and memory. Cap at 3000 nodes  #TODO: implement this
    "max_subgraph_size": 4000,
    "reconstruct": False,
    "reconstruction_mode": "STRND",  # STRND, ggvec, landmark_isomap, PyMDE, MDS

    "spatial_coherence_validation": {"spatial_constant": True, "network_dimension": True, "gram_matrix": True, "fast_gram_matrix": False, "sample_gram_matrix": False},
    "community_detection": False,
    "handle_all_subgraphs": False,
    'plot_original_image': True,
    'plot_reconstructed_image': False,

    # Make sure to tune the parameters for weighted graph (set everything to True, weight threshold nonzero maybe)
    "weighted": False,
    "weight_threshold": 0,
    "weight_to_distance": False,
    "weight_to_distance_fun": "exp",  #TODO: implement this (it is done for creation but not for regular)
    "verbose": False,
}

# Settings specific to simulation scenarios
simulation = {
    "num_points": 2000,
    "intended_av_degree": 10,  # set to 200 for weighted graphs
    "L": 1, # system size
    "max_false_edge_length": None,   # normally None, just to restrict false edge length for analysis
    "point_mode": 'circle',  # circle, square, triangle, star, ring
    "density_anomalies": False,
}


# Settings specific to experimental scenarios
experiment = {
    # pixelgen_example_graph.csv  #edge_list_nbead_0_filtering_march_8.csv, # edge_list_us_counties.csv # weinstein_data_corrected_february.csv,
    # weinstein_data_corrected_february_edge_list_and_original_distance_quantile_0.05.csv
    # weinstein_data_corrected_february_edge_list_and_original_distance_selected_square_region_quantile_0.1.csv
    # pixelgen_processed_edgelist_Sample07_pbmc_CD3_capped_cell_3_RCVCMP0000344.csv'
    # slidetag_31may2024.csv
    # Sample01_human_pbmcs_unstimulated_component_RCVCMP0001392_edgelist.csv --> best mpx data
    "edge_list_title": 'edge_list_weighted.csv',  # example_edge_list.pickle, edge_list_distance_150_filtering_goodindex_simon.csv, nbead_7_goodindex_simon.csv, edge_list_nbead_4_filtering.csv, subgraph_0_nodes_2053_edges_2646_degree_2.58.pickle (erik's data)
    "original_positions_available": False,
}
