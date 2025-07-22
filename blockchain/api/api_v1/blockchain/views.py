from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/", name="View blockchain")
async def blockchain(request: Request):
    node = request.app.state.node
    return node.blockchain.to_dict()


@router.get("/quantum-metrics/", name="View quantum annealing metrics")
async def quantum_metrics(request: Request):
    """Get quantum annealing consensus metrics"""
    node = request.app.state.node
    return node.blockchain.get_quantum_metrics()
