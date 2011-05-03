from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import HTMLParser
import re
import urlparse


UNLIKELY_CANDIDATES = re.compile(r"combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter", re.I)
OK_MAYBE_ITS_A_CANDIDATE = re.compile(r"and|article|body|column|main|shadow", re.I)
POSITIVE = re.compile("article|body|content|entry|hentry|main|page|pagination|post|text|blog|story", re.I)
NEGATIVE = re.compile("combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget", re.I)
EXTRANEOUS = re.compile("print|archive|comment|discuss|e[\-]?mail|share|reply|all|login|sign|single", re.I)
DIV_TO_P_ELEMENTS = re.compile(r"^(a|blockquote|dl|div|img|ol|p|pre|table|ul)$", re.I)
REPLACE_BRS_RE = re.compile(r"<br.*?/?>\s*?<br.*?/?>", re.I)
REPLACE_FONTS = re.compile(r"(<(/?)font.*?>)", re.I)
VIDEOS = re.compile(r"http://(www\.)?(youtube|vimeo)\.com", re.I)
SPACES = re.compile(r"\s+")
SCRIPTS_RE = re.compile(r"<script.*?>.*?</script>", re.I | re.DOTALL)
COMMENTS_RE = re.compile(r"<!--.*?-->", re.I | re.DOTALL)

class ReadabilityException(Exception):
    pass


class Readability:

    FLAG_STRIP_UNLIKELYS = 1
    FLAG_WEIGHT_CLASSES = 2
    FLAG_CLEAN_CONDITIONALLY = 3
    
    def __init__(self, link, html):

        self.flags = [self.FLAG_STRIP_UNLIKELYS,
                      self.FLAG_WEIGHT_CLASSES,
                      self.FLAG_CLEAN_CONDITIONALLY]
        
        self.link = link
        html = self.remove_scripts(html)
        html = self.remove_comments(html)
        
        try:
            self.soup = self.prepare_document(html)
        except HTMLParser.HTMLParseError:
            raise ReadabilityException()
    
    def remove_scripts(self, html):
        return SCRIPTS_RE.sub("", html)

    def remove_comments(self, html):
        return COMMENTS_RE.sub("", html)
        
    def prepare_document(self, html):
        
        # Replace double brs
        html = REPLACE_BRS_RE.sub(r"</p><p>", html)
        
        # Replace font tags
        html = REPLACE_FONTS.sub(r"<\1span>", html)
        
        soup = BeautifulSoup(html)
        
        # Stop the parsing if document contains frames
        if soup.find("frame"):
            raise ReadabilityException()
        
        # Remove all stylesheets
        for el in soup.findAll("style"):
            el.extract()
        for el in soup.findAll("link", attrs=dict(rel="stylesheet")):
            el.extract()
            
        return soup
        
    def get_inner_text(self, tag):
        s = u""
        for el in tag.contents:
            if isinstance(el, NavigableString):
                s += unicode(el)
            elif isinstance(el, Tag):
                s += self.get_inner_text(el)
        return SPACES.sub(u" ", s).strip()
    
    def get_class_weight(self, node):
        if self.FLAG_WEIGHT_CLASSES not in self.flags:
            return 0
        weight = 0
        class_name = node.get("class", None)
        if class_name:
            if NEGATIVE.search(class_name):
                weight -= 25
            if POSITIVE.search(class_name):
                weight += 25
        id = node.get("id", None)
        if id:
            if NEGATIVE.search(id):
                weight -= 25
            if POSITIVE.search(id):
                weight += 25
        return weight
    
    def initialize_node(self, node):
        node.readability = {"content_score": 0};         
        if node.name == "div":
            node.readability["content_score"] += 5
        elif node.name in ("pre", "td", "blockquote"):
            node.readability["content_score"] += 3
        elif node.name in ("address", "ol", "ul", "dl", "dd", "dt", "li", "form"):
            node.readability["content_score"] -= 3
        elif node.name in ("h1", "h2", "h3", "h4", "h5", "h6", "th"):
            node.readability["content_score"] -= 5
           
        node.readability["content_score"] += self.get_class_weight(node);
    
    def get_article_title(self):
        
        soup = self.soup
        orig_title = u""
        title = u""
        title_tag = soup.find("title") 
        
        if title_tag and title_tag.string:
            orig_title = title_tag.string.strip()
    
        if orig_title:
            if re.search(r"\s[\|\-]\s", orig_title):
                title_parts = re.split(r"\s[\|\-]\s", orig_title, 1)
                if len(title_parts[0].split()) > 2:
                    title = title_parts[0]
                else:
                    title = title_parts[1]
            elif re.search(r" &laquo; ", orig_title):
                title = re.split(r" &laquo; ", orig_title)[0]
            elif re.search(r" &raquo; ", orig_title):
                title = re.split(r" &raquo; ", orig_title)[-1]
            elif 150 < len(orig_title) < 15:
                h_ones = soup.findAll("h1")
                if len(h_ones) == 1:
                    title = self.get_inner_text(h_ones[0])
                
        if len(title.split()) < 4:
            title = orig_title
                
        title = title.strip()
    
        if not title:
            raise ReadabilityException()
        
        return title
    
    def get_meta_description(self):
        soup = self.soup
        description_tag = soup.find("meta", {"name": "description"})
        if description_tag and description_tag["content"]:
            return description_tag["content"].strip()
        return None
        
    def get_article_text(self):
        
        soup = self.soup
        orig_html = soup.renderContents()
        body = soup.body
        
        if not body:
            raise ReadabilityException()
        
        if self.FLAG_STRIP_UNLIKELYS in self.flags:
            for node in body.findAll(True, attrs={"id":UNLIKELY_CANDIDATES}):
                if (node.get("class") and OK_MAYBE_ITS_A_CANDIDATE.search(node["class"])) or \
                    OK_MAYBE_ITS_A_CANDIDATE.search(node["id"]):
                    continue
                node.extract()
                
            for node in body.findAll(True, attrs={"class":UNLIKELY_CANDIDATES}):
                if OK_MAYBE_ITS_A_CANDIDATE.search(node["class"]) or \
                    (node.get("id") and OK_MAYBE_ITS_A_CANDIDATE.search(node["id"])):
                    continue
                node.extract()
    
        # Replace div with paragraphs
        for div in body.findAll("div"):
            if not len(div.findAll(DIV_TO_P_ELEMENTS)):
                div.name = "p"
            
        nodes_to_score = body.findAll(re.compile("^p|td|pre$", re.I))
        
        # Loop through all paragraphs, and assign a score to them based on how content-y they look.
        # Then add their score to their parent node.
        # 
        # A score is determined by things like number of commas, class names, etc. Maybe eventually link density.
        candidates = []
        for node in nodes_to_score:
            parent = node.parent
            if not parent:
                continue
            grand_parent = parent and parent.parent
            inner_text = self.get_inner_text(node)
            
            # If this paragraph is less than 25 characters, don't even count it.
            if len(inner_text) < 25:
                continue
            
            # Initialize readability data for the parent.
            if not getattr(parent, "readability", None):
                self.initialize_node(parent)
                candidates.append(parent)
                
            #  Initialize readability data for the grandparent.
            if grand_parent and not getattr(grand_parent, "readability", None):
                self.initialize_node(grand_parent)
                candidates.append(grand_parent)
                
            content_score = 0  
            
            # Add a point for the paragraph itself as a base.
            content_score += 1
            
            # Add points for any commas within this paragraph
            content_score += inner_text.count(",")
            
            # For every 100 characters in this paragraph, add another point. Up to 3 points.
            content_score += min(len(inner_text) / 100, 3)
            
            # Add the score to the parent. The grandparent gets half.
            parent.readability["content_score"] += content_score
            if grand_parent:
                grand_parent.readability["content_score"] += content_score / 2
            
        # After we've calculated scores, loop through all of the possible candidate nodes we found
        # and find the one with the highest score.    
        top_candidate = None
        for candidate in candidates:
            # Scale the final candidates score based on link density. Good content should have a
            # relatively small link density (5% or less) and be mostly unaffected by this operation.
            candidate.readability["content_score"] = candidate.readability["content_score"] * (1 - self.get_link_density(candidate))
            if not top_candidate or top_candidate.readability["content_score"] < candidate.readability["content_score"]:
                top_candidate = candidate

        # If we still have no top candidate, just use the body as a last resort.
        # We also have to copy the body node so it is something we can modify.
        if not top_candidate:
            top_candidate = Tag(soup, "div")
            for c in body:
                top_candidate.append(c.extract())
            body.append(top_candidate)
            self.initialize_node(top_candidate)
        
        article = BeautifulSoup("<div></div>").div

        # Now that we have the top candidate, look through its siblings for content that might also be related.
        # Things like preambles, content split by ads that we removed, etc.                 
        sibling_score_threshold = max(10, top_candidate.readability["content_score"] * 0.2)
        top_candidate_class = top_candidate.get("class", None)

        for sibling_node in top_candidate.parent:
            if not isinstance(sibling_node, Tag):
                continue
            
            append = False
            
            if sibling_node == top_candidate:
                append = True
            else:
                content_bonus = 0
                # Give a bonus if sibling nodes and top candidates have the example same classname
                if top_candidate_class and top_candidate_class == sibling_node.get("class", None):
                    content_bonus += top_candidate.readability["content_score"] * 0.2
                if getattr(sibling_node, "readability", None) and (sibling_node.readability["content_score"] + content_bonus) >= sibling_score_threshold:
                    append = True
                
                if sibling_node.name == "p":
                    link_density = self.get_link_density(sibling_node)
                    node_content = self.get_inner_text(sibling_node)
                    node_length = len(node_content)
                    if node_length > 80 and link_density < 0.25:
                        append = True
                    elif node_length <= 80 and link_density == 0 and re.search(r"\.( |$)", node_content):
                        append = True
                    
            if append:
                if sibling_node.name not in ("div", "p"):
                    # We have a node that isn't a common block level element, like a form or td tag. Turn it into a div so it doesn't get filtered out later by accident.
                    sibling_node.name = "div"
                    
                # To ensure a node does not interfere with readability styles, remove its classnames
                if sibling_node.get("class", None):
                    del sibling_node["class"]
                article.append(sibling_node)
                    

        if len(article.renderContents()) < 250:
            soup = BeautifulSoup(orig_html)
            if self.FLAG_STRIP_UNLIKELYS in self.flags:
                self.flags.remove(self.FLAG_STRIP_UNLIKELYS)
                return self.get_article_text()
            elif self.FLAG_WEIGHT_CLASSES in self.flags:
                self.flags.remove(self.FLAG_WEIGHT_CLASSES)
                return self.get_article_text()
            elif self.FLAG_CLEAN_CONDITIONALLY in self.flags:
                self.flags.remove(self.FLAG_CLEAN_CONDITIONALLY)
                return self.get_article_text()
            else:
                raise ReadabilityException()
            
        self.prepare_article(article)
            
        return article.renderContents(encoding=None)
    
    def get_link_density(self, node):
        links = node.findAll("a")
        length = len(self.get_inner_text(node))
        if not length:
            return 1
        link_length = 0
        for link in links:
            link_length += len(self.get_inner_text(link))
        return link_length / length
    
    def prepare_article(self, article):
        self.clean_styles(article)
        self.kill_breaks(article)
    
        self.clean_conditionally(article, "form")
        self.clean(article, "object")
        self.clean(article, "h1")

        # If there is only one h2, they are probably using it
        # as a header and not a subheader, so remove it since we already have a header.
        if len(article.findAll("h2")) == 1:
            self.clean(article, "h2")
        
        self.clean(article, "iframe")
        self.clean_headers(article)
        
        # Do these last as the previous stuff may have removed junk that will affect these
        self.clean_conditionally(article, "table")
        self.clean_conditionally(article, "ul")
        self.clean_conditionally(article, "div")
        
        # Remove extra paragraphs
        for p in reversed(article.findAll("p")):
            img = len(p.findAll("img"))
            embed = len(p.findAll("embed"))
            object = len(p.findAll("object"))
            if not img and not embed and not object and not self.get_inner_text(p):
                p.extract()
    
        if self.link:
            self.fix_links(article, self.link)
    
    def clean_styles(self, node):
        for t in node.findAll(style=True):
            del t["style"]
    
    def kill_breaks(self, article):
        for br in article.findAll("br"):
            prev = br.previousSibling
            while isinstance(prev, NavigableString):
                if not unicode(prev).replace("&nbsp;", "").strip() and prev.previousSibling:
                    prev = prev.previousSibling
                else:
                    prev = None
            
            next = br.nextSibling
            while isinstance(next, NavigableString):
                if not unicode(next).replace("&nbsp;", "").strip() and next.nextSibling:
                    next = next.nextSibling
                else:
                    next = None

            if (prev and prev.name == "br") or (next and next.name == "p"):
                br.extract()
    
    def clean_conditionally(self, node, tag):
        if self.FLAG_CLEAN_CONDITIONALLY not in self.flags:
            return
        for tag in reversed(node.findAll(tag)):
            weight = self.get_class_weight(tag)
            tag_content = self.get_inner_text(tag)
            content_score = (getattr(tag, "readability", None) or {}).get("content_score", 0)
            if weight + content_score < 0:
                tag.extract()
            elif tag_content.count(",") < 10:
                # If there are not very many commas, and the number of
                # non-paragraph elements is more than paragraphs or other ominous signs, remove the element.
                p = len(tag.findAll("p"))
                img = len(tag.findAll("img"))
                li = len(tag.findAll("li")) - 100
                input = len(tag.findAll("input"))
                embeds = len(tag.findAll("embed")) - len(tag.findAll("embed", src=VIDEOS))
                
                link_density = self.get_link_density(tag)
                content_length = len(tag_content)
                if (img > p) or \
                   (li > p and tag.name not in ("ul", "ol")) or \
                   (input > p / 3) or \
                   (content_length < 25 and (img == 0 or img > 2)) or \
                   (weight < 25 and link_density > 0.2) or \
                   (weight >= 25 and link_density > 0.5) or \
                   (embeds == 1 and content_length < 75 or embeds > 1):
                    tag.extract()
    
    def clean(self, node, tag):
        for tag in node.findAll(tag):
            # Allow youtube and vimeo videos through as people usually want to see those.
            if tag.name in ("embed", "object"):
                for value in tag.attrs.values():
                    if VIDEOS.search(value):
                        continue
                if VIDEOS.search(tag.renderContents()):
                    continue
                    
            tag.extract()
    
    def clean_headers(self, node):
        for header_tag in ("h1", "h2"):
            for header in node.findAll(header_tag):
                if (self.get_class_weight(header) < 0 or self.get_link_density(header) > 0.33):
                    header.extract()
    
    def fix_links(self, parent, link):
        tags = parent.findAll(True)
        
        for t in tags:
            if (t.has_key("href")):
                t["href"] = urlparse.urljoin(link, t["href"])
            if (t.has_key("src")):
                t["src"] = urlparse.urljoin(link, t["src"])
    