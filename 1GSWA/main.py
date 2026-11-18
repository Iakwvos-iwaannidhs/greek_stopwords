
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
import json,csv,re,unicodedata
from collections import Counter
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class App:
    def __init__(self,root):
        self.root=root
        self.root.title('Greek Stop Word Analyzer')
        self.counter=Counter()
        self.metrics={}
        ttk.Button(root,text='Analyze Files',command=self.analyze).pack(pady=5)
        ttk.Button(root,text='Export Excel',command=self.export_excel).pack(pady=5)
        ttk.Button(root,text='Export PDF',command=self.export_pdf).pack(pady=5)
        self.txt=tk.Text(root,height=15,width=90)
        self.txt.pack()
        self.fig,(self.ax)=plt.subplots(figsize=(6,4))
        self.canvas=FigureCanvasTkAgg(self.fig,master=root)
        self.canvas.get_tk_widget().pack(fill='both',expand=True)

    def normalize(self,t):
        t=t.lower()
        t=''.join(c for c in unicodedata.normalize('NFD',t) if unicodedata.category(c)!='Mn')
        t=t.replace('ς','σ')
        return re.sub(r'[^α-ω\s]',' ',t)

    def load_sw(self):
        with open('greek_stopwords.json',encoding='utf8') as f:
            return set(self.normalize(w) for w in json.load(f)['stopwords'])

    def analyze(self):
        files=filedialog.askopenfilenames(filetypes=[('Text','*.txt')])
        if not files:return
        sw=self.load_sw(); all_words=[]; self.counter=Counter()
        for fp in files:
            text=open(fp,encoding='utf8').read()
            words=self.normalize(text).split(); all_words.extend(words)
            for w in words:
                if w in sw:self.counter[w]+=1
        total=len(all_words); stop=sum(self.counter.values())
        self.metrics={'Total Words':total,'Stop Words':stop,'Density %':round((stop/total*100) if total else 0,2),'Unique Stop Words':len(self.counter)}
        self.txt.delete('1.0','end')
        for k,v in self.metrics.items(): self.txt.insert('end',f'{k}: {v}')
        self.ax.clear()
        top=self.counter.most_common(10)
        if top:
            self.ax.bar([x[0] for x in top],[x[1] for x in top])
        self.canvas.draw()

    def export_excel(self):
        fn=filedialog.asksaveasfilename(defaultextension='.xlsx')
        if not fn:return
        with pd.ExcelWriter(fn,engine='openpyxl') as w:
            pd.DataFrame(list(self.metrics.items()),columns=['Metric','Value']).to_excel(w,sheet_name='Summary',index=False)
            pd.DataFrame(self.counter.items(),columns=['StopWord','Frequency']).to_excel(w,sheet_name='StopWords',index=False)

    def export_pdf(self):
        fn=filedialog.asksaveasfilename(defaultextension='.pdf')
        if not fn:return
        doc=SimpleDocTemplate(fn); styles=getSampleStyleSheet(); elems=[Paragraph('Greek Stop Word Analysis',styles['Title'])]
        for k,v in self.metrics.items(): elems.append(Paragraph(f'{k}: {v}',styles['BodyText']))
        elems.append(Spacer(1,12))
        for w,c in self.counter.most_common(20): elems.append(Paragraph(f'{w}: {c}',styles['BodyText']))
        doc.build(elems)

root=tk.Tk(); App(root); root.mainloop()
