# -------------------------------------------------------------------------------
# (c) Copyright 2023 Sony Semiconductor Israel, Ltd. All rights reserved.
#
#      This software, in source or object form (the "Software"), is the
#      property of Sony Semiconductor Israel Ltd. (the "Company") and/or its
#      licensors, which have all right, title and interest therein, You
#      may use the Software only in accordance with the terms of written
#      license agreement between you and the Company (the "License").
#      Except as expressly stated in the License, the Company grants no
#      licenses by implication, estoppel, or otherwise. If you are not
#      aware of or do not agree to the License terms, you may not use,
#      copy or modify the Software. You may use the source code of the
#      Software only for your internal purposes and may not distribute the
#      source code of the Software, any part thereof, or any derivative work
#      thereof, to any third party, except pursuant to the Company's prior
#      written consent.
#      The Software is the confidential information of the Company.
# -------------------------------------------------------------------------------

from .nnir_substitute_base import NnirSubstituteBase
from .absorb_quant_substitution import AbsorbQuantSubstitution
from .remove_dummy_nodes_substitution import RemoveDummyNodeSubstitution
from .merge_fully_connected_add_substitution import MergeFullyConnectedAndAddSubstitution
from .nms_outputs_substitution import NMSOutputsSubstitution
from .norm_substitution import NormSubstitution
from .remove_identity_like_substitution import RemoveIdentityLikeSubstitution
from .rsqrt_substitution import RsqrtSubstitution
from .single_nodes_substitution import SingleNodesSubstitution
from .const_topk_gather_substitution import ConstTopkGatherSubstitution

from .substitution_manager import SubstitutionManager
