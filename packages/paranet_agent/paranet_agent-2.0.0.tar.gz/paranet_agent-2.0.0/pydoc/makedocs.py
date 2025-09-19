import os
import yaml
import glob
import shutil
import dataclasses
import typing as t

import docspec
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.interfaces import Processor, Resolver

@dataclasses.dataclass
class SidebarProcessor(Processor):
    def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
        self.position = 1
        docspec.visit(modules, self._process)

    def _process(self, node: docspec.ApiObject):
        if isinstance(node, docspec.Module):
          name=node.name.rsplit(".", 1)[-1]
          header = f"""---\nid: {name}\ntitle: {name.title()}\nsidebar_position: {self.position}\n---\n"""
          self.position += 1
          if not node.docstring:
              node.docstring = docspec.Docstring(location=node.location, content=header)
          else:
              node.docstring.content = header + "\n" + node.docstring.content

@dataclasses.dataclass
class PrivateProcessor(Processor):
    def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
        def m(obj):
            if obj.docstring and '@private' in obj.docstring.content:
              print(obj.name, obj.__class__.__name__)
              return False
            return True

        docspec.filter_visit(t.cast(t.List[docspec.ApiObject], modules), m, order="post")

config = PydocMarkdown()
config.load_config(yaml.safe_load('config.yaml'))

config.processors.append(SidebarProcessor())
config.processors.append(PrivateProcessor())

mods = config.load_modules()
config.process(mods)
config.render(mods)

for fullname in glob.glob('./sdk/paranet_agent/*.md'):
    filename = os.path.basename(fullname)
    basename = os.path.splitext(filename)[0]
    dst = os.path.join('../../docs_external', basename)
    os.makedirs(dst, exist_ok=True)
    dst = os.path.join(dst, 'index.md')
    shutil.copyfile(fullname, dst)
