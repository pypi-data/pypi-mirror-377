from pathlib import Path

import lumen.ai as lmai

from lumen_anndata.analysis import (
    ClustermapVisualization, LeidenComputation, ManifoldMapVisualization,
    RankGenesGroupsTracksplot,
)
from lumen_anndata.controls import CellXGeneSourceControls
from lumen_anndata.utils import upload_h5ad

PROMPTS_DIR = Path(__file__).parent / "prompts"

INSTRUCTIONS = """
You are an expert scientist working in Python, with a specialty using Anndata and Scanpy.
All of your answers must be grounded in the provided embedding context by citing specific entries where applicable.
Do not assume functions or APIs exist unless they are present in the context.
If the user asks about something not explicitly found in the context, explain
that it could not be located and suggest any related or alternative entries
that were found. When you refer to context entries, cite them clearly
(e.g., by mentioning their documented signature or behavior). The
base URL is https://scanpy.readthedocs.io/en/stable/.

Prioritize accuracy over familiarity: even if a user asks about a well-known function,
do not describe or assume its behavior unless it appears in the context.
Prefer similar or equivalent matches in the context over standard assumptions.
If you cannot find a match or give a confident answer, acknowledge it
and suggest other relevant entries that might help the user.
"""


def build_ui():
    db_uri = str(Path(__file__).parent / "embeddings" / "scanpy.db")
    vector_store = lmai.vector_store.DuckDBVectorStore(uri=db_uri, embeddings=lmai.embeddings.HuggingFaceEmbeddings())
    doc_lookup = lmai.tools.VectorLookupTool(vector_store=vector_store, n=3)

    ui = lmai.ExplorerUI(
        agents=[lmai.agents.ChatAgent(tools=[doc_lookup], template_overrides={"main": {"instructions": INSTRUCTIONS}})],
        table_upload_callbacks={
            ".h5ad": upload_h5ad,
        },
        analyses=[ClustermapVisualization, ManifoldMapVisualization, LeidenComputation, RankGenesGroupsTracksplot],
        source_controls=CellXGeneSourceControls,
        log_level="DEBUG",
    )
    return ui
