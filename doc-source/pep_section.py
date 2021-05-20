# stdlib
from typing import Dict, List, Tuple

# 3rd party
from docutils import nodes
from docutils.nodes import Node, system_message, unescape
from docutils.parsers.rst.states import Inliner
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util.docutils import ReferenceRole, SphinxRole


class PEP(ReferenceRole):

	def run(self) -> Tuple[List[Node], List[system_message]]:
		target_id = "index-%s" % self.env.new_serialno("index")
		entries = [("single", _("Python Enhancement Proposals; PEP %s") % self.target, target_id, '', None)]

		index = addnodes.index(entries=entries)
		target = nodes.target('', '', ids=[target_id])
		self.inliner.document.note_explicit_target(target)

		try:
			refuri = self.build_uri()
			reference = nodes.reference('', '', internal=False, refuri=refuri, classes=["pep"])
			if self.has_explicit_title:
				reference += nodes.inline(self.title, self.title)
			else:
				title = "PEP " + self.title
				reference += nodes.strong(title, title)
		except ValueError as e:
			print(self.title, self.target, e)
			msg = self.inliner.reporter.error("invalid PEP number %s" % self.target, line=self.lineno)
			prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
			return [prb], [msg]

		return [index, target, reference], []

	def build_uri(self) -> str:
		base_url = self.inliner.document.settings.pep_base_url
		ret = self.target.split('#', 1)
		if len(ret) == 2:
			return base_url + "pep-%04d#%s" % (int(ret[0]), ret[1])
		else:
			return base_url + "pep-%04d" % int(ret[0])


class PEP621Section(PEP):

	def __call__(
			self,
			name: str,
			rawtext: str,
			text: str,
			lineno: int,
			inliner: Inliner,
			options: Dict = {},
			content: List[str] = []
			) -> Tuple[List[Node], List[system_message]]:
		# if the first character is a bang, don't cross-reference at all
		self.disabled = text.startswith('!')

		# matched = self.explicit_title_re.match(text)
		# if matched:
		# 	text = f"{unescape(matched.group(1))} <621#{unescape(matched.group(2))}>"
		# 	rawtext = f":pep:`{text}`"
		# else:
		# 	text = f"{unescape(text)} <621#{unescape(text)}>"
		# 	rawtext = f":pep:`{text}`"
		#
		# print(repr(text))
		#
		# return super().__call__(name, rawtext, text, lineno, inliner, options, content)

		matched = self.explicit_title_re.match(text)
		if matched:
			self.has_explicit_title = True
			self.title = unescape(matched.group(1))
			self.target = f"621#{unescape(matched.group(2))}"
		else:
			self.has_explicit_title = True
			self.title = unescape(text)
			self.target = f"621#{unescape(text)}"

		print(text, self.title, self.target)

		return SphinxRole.__call__(self, name, rawtext, text, lineno, inliner, options, content)


def setup(app: Sphinx):
	# 3rd party
	from docutils.parsers.rst import roles

	roles.register_local_role("pep", PEP())
	roles.register_local_role("pep621", PEP621Section())
