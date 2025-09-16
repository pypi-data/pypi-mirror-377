import torch

from loguru import logger

from syndrilla.matrix import create_parity_matrix


class create():
    """
    This class creates a lx logical check.
    """
    def __init__(self, 
                 check_cfg, 
                 **kwargs) -> None:
        pass


    def check(self, e_v_total, error_vector, lz_matrix, converge=None):
        logger.info(f'Measuring logical check rate.')
        e_v_total = e_v_total.to(error_vector.device)
        lz_matrix = torch.tensor(lz_matrix, device = error_vector.device, dtype = error_vector.dtype).unsqueeze(0)

        logical_check = ((e_v_total + error_vector)%2).to(e_v_total.dtype).unsqueeze(2)
        # lx logical check is obtained by matrix multiplication between lx matrix with ((e_hat + e) % 2) (need to use matmul)
        logical_check = torch.where(torch.sum((lz_matrix @ logical_check)%2, dim=(1, 2)) > 0, 1, 0)

        # converge represents whether the sample converges in decoder before reaching the maximum iteration
        if converge is not None:
            converge_index = torch.where(converge == 0)[0]
            logical_check[converge_index] = 1
        logger.info(f'Logical check rate measurement complete.')
        return logical_check    
    
    