# import libs
from typing import (
    Literal
)
from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


class Component(BaseModel):
    """
    Component model for input validation

    Attributes
    ----------
    name : str
        Name of the component.
    formula : str
        Chemical formula of the component.
    state : Literal['g', 'l', 's', 'aq']
        State of the component: 'g' for gas, 'l' for liquid, 's' for solid, 'aq' for aqueous.
    mole_fraction : float, optional
        Mole fraction of the component in a mixture, if applicable. Default is 1.0.
    """
    name: str = Field(..., description="Name of the component")
    formula: str = Field(..., description="Chemical formula of the component")
    state: Literal['g', 'l', 's', 'aq'] = Field(
        ...,
        description="State of the component: 'g' for gas, 'l' for liquid, 's' for solid, 'aq' for aqueous"
    )
    mole_fraction: float = Field(
        default=1.0,
        description="Mole fraction of the component in a mixture, if applicable"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )
