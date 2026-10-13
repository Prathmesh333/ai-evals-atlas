"""Detailed SVG figures with explicit edges, branch points, and explanatory labels."""
from html import escape as e

DETAILS = {
 'attention-mask': ('language-models', 'Which tokens can attend to which?', 'Each row is a query position. Filled cells are visible keys. Future positions are masked before softmax.'),
 'transformer-block': ('tiny-transformer', 'Inside one pre-normalized transformer block', 'Layer normalization precedes each sublayer. Each residual addition preserves a direct path for the block input. Repeat the block, then apply final normalization and the output head.'),
 'data-splits': ('dataset-design', 'Keep three jobs separate', 'Fit weights on training data. Select settings with validation data. Freeze choices before the final test. Do not feed test results back into selection.'),
 'confusion-matrix': ('metrics', 'Read a confusion matrix', 'Rows show the actual class. Columns show the prediction. Precision divides true positives by the predicted-positive column. Recall divides true positives by the actual-positive row.'),
 'rag-pipeline': ('rag-agents', 'Retrieval has an indexing path and a query path', 'Index permitted documents in advance. At query time, retrieve relevant chunks, apply access checks, and provide evidence to the generator. Evaluate retrieval and answer support separately.'),
 'distributed-workers': ('scaling-training', 'Data parallel training', 'Replicas process different batches. An all-reduce combines gradients before each replica applies the update. Other parallelism strategies partition different parts of the work.'),
 'platform-architecture': ('eval-platform', 'The evaluation service architecture', 'The runner reads versioned inputs and dispatches trials. Preserve raw artifacts before applying graders. Reports link back to the run and case identifiers.'),
 'lora-path': ('post-training', 'A low-rank update beside a frozen weight', 'The output combines the frozen projection Wx and a learned low-rank update BAx, scaled by a chosen factor. This shows one adapted projection, not an entire model.'),
}


class Drawing:
    def __init__(self,key,title,description,height=370):
        self.key=key
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 710 {height}" role="img" aria-labelledby="t-{key} d-{key}"><title id="t-{key}">{e(title)}</title><desc id="d-{key}">{e(description)}</desc><defs><marker id="a-{key}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10" fill="#718096"/></marker></defs>']
    def box(self,x,y,w,title,sub='',h=62,accent=False):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{("#eef4fd" if accent else "#fff")}" stroke="#b9c4d0"/>')
        self.text(x+w/2,y+25,title,14,True,'middle')
        if sub:self.text(x+w/2,y+46,sub,11,False,'middle')
    def text(self,x,y,text,size=12,bold=False,anchor='start',color='#536170'):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{600 if bold else 400}" fill="{("#1c2938" if bold else color)}">{e(text)}</text>')
    def path(self,d,dashed=False):
        dash = 'stroke-dasharray="5 4"' if dashed else ''
        self.parts.append(f'<path d="{d}" fill="none" stroke="#718096" stroke-width="1.5" {dash} marker-end="url(#a-{self.key})"/>')
    def end(self):return ''.join(self.parts)+'</svg>'


def detailed_svg(key):
    chapter,title,description=DETAILS[key]
    height=510 if key=='transformer-block' else 370
    d=Drawing(key,title,description,height)
    if key=='attention-mask':
        d.text(195,24,'Key positions →',12,True)
        for c in range(5):d.text(209+c*46,53,str(c+1),12,False,'middle')
        for r in range(5):
            d.text(166,88+r*46,str(r+1),12,False,'middle')
            for c in range(5):
                fill='#d8e6f8' if c<=r else '#f3f4f6'
                d.parts.append(f'<rect x="{188+c*46}" y="{65+r*46}" width="42" height="42" rx="3" fill="{fill}" stroke="#ccd5df"/>')
                d.text(209+c*46,91+r*46,'✓' if c<=r else '×',14,False,'middle')
        d.text(25,169,'Query',12,True);d.text(25,188,'position ↓',12)
        d.text(455,128,'Position 3 can use',13,True);d.text(455,151,'positions 1, 2, and 3.',12)
        d.text(455,191,'It cannot see 4 or 5.',12)
        d.text(188,326,'Mask the future before computing attention weights.',12)
    elif key=='transformer-block':
        for y,title,sub in [(18,'Input x','Token representations'),(100,'LayerNorm → attention','Causal multi-head attention'),(198,'Add residual','x + attention(norm(x))'),(290,'LayerNorm → MLP','Position-wise transformation'),(390,'Add residual','Previous state + MLP output')]:
            d.box(215,y,280,title,sub)
        for y,yy in [(80,92),(162,190),(260,282),(352,382)]:d.path(f'M355 {y} V{yy}')
        d.path('M215 48 H130 V229 H207');d.text(30,155,'Residual x',12)
        d.path('M495 228 H570 V421 H503');d.text(579,325,'Residual',12)
        d.path('M355 452 V482');d.text(355,502,'Next block / final normalization and output head',12,False,'middle')
    elif key=='data-splits':
        d.box(225,16,260,'Group + deduplicate','Then split the source documents',accent=True)
        for x,title,sub in [(20,'Training','Fit parameters'),(255,'Validation','Choose settings'),(490,'Test','Final estimate')]:
            d.box(x,145,200,title,sub)
            d.path(f'M355 78 V108 H{x+100} V137')
        d.path('M120 207 V262 H347');d.box(355,232,200,'Frozen candidate','Model + configuration')
        d.path('M355 207 V224');d.path('M590 207 V323 H455 V302')
        d.text(30,284,'Learn weights',11);d.text(502,346,'Evaluate once choices are fixed',11,False,'middle')
    elif key=='confusion-matrix':
        d.text(355,24,'Predicted class',13,True,'middle')
        d.text(235,64,'Positive',12,True,'middle');d.text(445,64,'Negative',12,True,'middle')
        d.text(30,122,'Actual +',12,True);d.text(30,220,'Actual −',12,True)
        d.box(140,82,190,'TP = 8','Correct positive',80,True);d.box(350,82,190,'FN = 2','Missed positive',80)
        d.box(140,180,190,'FP = 4','False alarm',80);d.box(350,180,190,'TN = 86','Correct negative',80,True)
        d.text(140,305,'Precision = 8 / (8 + 4) = 66.7%',13)
        d.text(140,331,'Recall = 8 / (8 + 2) = 80.0%',13)
        d.text(560,122,'Positive row',11);d.text(560,144,'denominator',11);d.text(560,163,'for recall',11)
    elif key=='rag-pipeline':
        d.text(20,24,'INDEXING',10,True)
        d.box(20,44,190,'Permitted documents','Split into chunks');d.box(255,44,190,'Embedding model','Vectors for chunks');d.box(490,44,190,'Search index','Vectors + text + metadata')
        d.path('M210 75 H247');d.path('M445 75 H482')
        d.text(20,156,'QUERY TIME',10,True)
        d.box(20,180,190,'Question','Query representation');d.box(255,180,190,'Retrieve + authorize','Select relevant evidence');d.box(490,180,190,'Generator','Question + evidence')
        d.path('M210 211 H247');d.path('M445 211 H482');d.path('M585 106 V135 H355 V172')
        d.path('M585 242 V307 H363');d.box(150,276,205,'Answer + citations','Check correctness + support')
    elif key=='distributed-workers':
        d.box(235,15,240,'Versioned training data','Different batch per worker',accent=True)
        for x,n in [(20,1),(255,2),(490,3)]:
            d.box(x,126,190,f'Worker {n}','Forward + backward')
            d.path(f'M355 77 V100 H{x+95} V118')
            d.path(f'M{x+95} 188 V222 H355 V248')
        d.box(235,256,240,'All-reduce gradients','Then update every replica')
        d.path('M475 287 H697 V157 H688',True)
        d.path('M235 287 H8 V157 H12',True)
        d.path('M420 256 V210 H440 V196',True)
        d.text(355,350,'Each worker holds the same model; data batches differ.',12,False,'middle')
    elif key=='platform-architecture':
        d.box(20,20,190,'Dataset registry','Immutable case versions');d.box(20,120,190,'Run manifest','Model + grader + budget')
        d.box(255,70,190,'Scheduler / runner','Trials + retries + limits',accent=True);d.box(490,70,190,'Isolated workers','Model adapters + tools')
        d.path('M210 51 H230 V91 H247');d.path('M210 151 H230 V113 H247');d.path('M445 101 H482')
        d.box(490,240,190,'Artifact storage','Outputs + state + traces');d.box(255,240,190,'Versioned graders','Per-case scores');d.box(20,240,190,'Decision report','Slices + uncertainty')
        d.path('M585 132 V232');d.path('M490 271 H453');d.path('M255 271 H218')
        d.text(20,351,'Every artifact retains the run ID and case ID.',12)
    elif key=='lora-path':
        d.box(20,150,120,'Input x','');d.box(230,45,220,'Frozen W','Base projection')
        d.box(200,240,150,'Train A','Down-project');d.box(390,240,150,'Train B','Up-project')
        d.box(565,150,125,'Add','Output y',accent=True)
        d.path('M140 181 H168 V76 H222');d.path('M140 181 H168 V271 H192')
        d.path('M350 271 H382');d.path('M450 76 H627 V142');d.path('M540 271 H627 V220')
        d.text(280,350,'y = Wx + scale × BAx',16,True);d.text(478,227,'Scale update',11)
    return d.end()


def detailed_figure(key):
    _,title,description=DETAILS[key]
    return f'<figure class="diagram">{detailed_svg(key)}<figcaption><strong>{e(title)}.</strong> {e(description)} <a href="assets/diagrams/{key}.svg" download>Download SVG</a></figcaption></figure>'
