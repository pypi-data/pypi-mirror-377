import pandas as pd
from synthcity.plugins.core.dataloader import GenericDataLoader
from synthcity.plugins import Plugins

from ..base import TabularBaseGenerator


class BNGenerator(TabularBaseGenerator):
    name = "bn"

    def __init__(
        self,
        struct_learning_n_iter: int = 1000,
        struct_learning_search_method: str = "tree_search",  # hillclimb, pc, tree_search, mmhc, exhaustive
        struct_learning_score: str = "k2",  # k2, bdeu, bic, bds
        struct_max_indegree: int = 4,
        encoder_max_clusters: int = 10,
        encoder_noise_scale: float = 0.1,
        random_state: int = 0,
        **kwargs,
    ):
        super().__init__(random_state=random_state, **kwargs)
        self.model = Plugins().get(
            "bayesian_network",
            struct_learning_n_iter=struct_learning_n_iter,
            struct_learning_search_method=struct_learning_search_method,
            struct_learning_score=struct_learning_score,
            struct_max_indegree=struct_max_indegree,
            encoder_max_clusters=encoder_max_clusters,
            encoder_noise_scale=encoder_noise_scale,
            random_state=random_state,
        )

    def _fit_model(self, X: pd.DataFrame, discrete_features: list):

        loader = GenericDataLoader(
            X,
            target_column=self.target_column,
            train_size=1,
            random_state=self.random_state,
        )
        self.model.fit(loader)

    def _generate_data(self, n: int):
        syn = self.model.generate(n)
        return syn.dataframe()
