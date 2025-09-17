import inspect
from pprint import pprint
from typing import List, Dict, Callable, Union, Annotated, Any
import typer

from bixi.appcore import Workspace, PartialTyper
from bixi.utils.reflect import extract_function_table, dynamic_import


def run_partial_typer(entry: Union[Callable, List[Callable], Dict[str, Callable]], consume_argv: str = 'before') -> Any:
    cli = PartialTyper(entry, consume_argv=consume_argv)
    return cli()


def run_class(path: str = typer.Argument(..., help='The module to run, eg: aa.bbb.ccc.Application')) -> Any:
    cls = dynamic_import(*path.rsplit('.', 1))
    assert isinstance(cls, type)
    name2func = extract_function_table(cls)
    return run_partial_typer(list(name2func.values()))


def run_function(path: str = typer.Argument(..., help='The module to run, eg: aa.bbb.ccc.Application')) -> Any:
    func = dynamic_import(*path.rsplit('.', 1))
    assert isinstance(func, Callable)
    return run_partial_typer(func)


def list_runnable(path: str = typer.Argument(..., help='The module to run, eg: aa.bbb.ccc.Application')) -> None:
    obj = dynamic_import(*path.rsplit('.', 1))
    if isinstance(obj, type):
        name2func = extract_function_table(obj)
        print(f"Class {obj.__name__}:")
        for name, func in name2func.items():
            print(f"\t{name}: {list(inspect.signature(func).parameters.keys())}")
    elif isinstance(obj, Callable):
        print(f"Method {obj.__name__}: ", end='')
        pprint(inspect.signature(obj))
    else:
        raise NotImplemented


def list_workspace(
        search_root: Annotated[str, typer.Option(..., metavar='TEXT', help="Root directory for finding workspace file. Default is the current working directory.")] = None,
        prefix: Annotated[str, typer.Option(..., metavar='REGEX', help="Prefix.")] = None,
        name: Annotated[str, typer.Option(..., metavar='REGEX', help="Workspace name.")] = None,
        id: Annotated[str, typer.Option(..., metavar='REGEX', help="Workspace ID.")] = None,
        dirname: Annotated[str, typer.Option(..., metavar='REGEX', help="Directory name.")] = None,
        rootpath: Annotated[str, typer.Option(..., metavar='REGEX', help="Root path.")] = None,
        output_fields: Annotated[List[str], typer.Option(..., '-of', help="Output filter.")] = None
) -> None:
    metadata_dict = Workspace.query_workspace_metadata(
        search_root=search_root,
        prefix=prefix,
        name=name,
        id=id,
        dirname=dirname,
        rootpath=rootpath
    )
    for i, (filepath_i, metadata_i) in enumerate(metadata_dict.items()):
        if output_fields:
            print(*[v for k, v in metadata_i.items() if k in output_fields])
        else:
            print(f"[{i + 1}] Workspace metadata at {filepath_i}:")
            pprint(metadata_i)


def main():
    run_partial_typer(entry=[run_class, run_function, list_runnable, list_workspace])


if __name__ == '__main__':
    main()
