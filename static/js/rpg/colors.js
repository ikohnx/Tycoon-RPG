window.RPGColors = (function() {
    const C = {
        g1: '#2a9e3a', g2: '#1e8830', g3: '#3cb858', g4: '#50c868', gd: '#1a7028', gdd: '#105818', gb: '#5a4830',
        g5: '#45d270', g6: '#0d4518', g7: '#88e898', g8: '#247a2e', g9: '#328c3a', g10: '#168020',
        p1: '#c8a870', p2: '#b89860', p3: '#a88850', p4: '#d8b880', pe: '#8a7040', pm: '#6e5838',
        p5: '#9e7838', p6: '#d4b478', p7: '#bca068',
        w1: '#1848a8', w2: '#2058c0', w3: '#103888', w4: '#2868d0', wf: '#90c0f0', ws: '#4070c0', wd: '#0c2870', wsp: '#c8e0ff',
        w5: '#3878e0', w6: '#0a1848', w7: '#1040a0', w8: '#5090d8', w9: '#183898',
        bk1: '#788098', bk2: '#687088', bk3: '#8890a8', bk4: '#9098b0', bkl: '#505868', bkd: '#404850', bkh: '#a0a8b8',
        bk5: '#303840', bk6: '#a8b0c0', bk7: '#586070', bk8: '#98a0b0',
        rf1: '#c84838', rf2: '#d85848', rf3: '#b83828', rf4: '#e86858', rfl: '#882018', rfh: '#f08878', rfs: '#981818',
        rf5: '#a83020', rf6: '#d04838',
        dr1: '#704828', dr2: '#886038', dr3: '#5a3818', drk: '#e8c840', drf: '#604020', drh: '#a87848',
        dr4: '#9a7050', dr5: '#503018',
        wn1: '#4898d0', wn2: '#68b8f0', wn3: '#3880b8', wnf: '#484858', wns: '#a8d8ff', wnc: '#c06048',
        wn4: '#5888b0', wn5: '#3068a0',
        wd1: '#886038', wd2: '#a07848', wd3: '#685028', wd4: '#b89058', wdg: '#504018', wdk: '#4a3820',
        wd5: '#907048', wd6: '#785830', wd7: '#c0a068',
        st1: '#708088', st2: '#8898a0', st3: '#586870', st4: '#98a8b0', stm: '#485058',
        st5: '#7888a0', st6: '#607078', st7: '#a0b0b8',
        tr1: '#187828', tr2: '#28a040', tr3: '#0e5818', tr4: '#38b858', trh: '#48c868', trs: '#084010', tk1: '#5a3818', tk2: '#704828', tk3: '#483010',
        tr5: '#1a6820', tr6: '#309848', tk4: '#624020',
        fr: '#e83848', fy: '#f0d020', fp: '#c040e8', fw: '#f0e8f0', fo: '#f09030', fb: '#4080f0',
        sg1: '#a87840', sg2: '#c89050', sg3: '#e0a860', sgp: '#5a3818', sgd: '#483010',
        pt1: '#4820a0', pt2: '#6830d0', pt3: '#9050f0', pt4: '#b878ff', ptg: '#d0a0ff',
        hg1: '#186828', hg2: '#208838', hg3: '#28a048', hg4: '#10501a', hgs: '#0c4014',
        ch1: '#d09830', ch2: '#a87828', ch3: '#886018', chl: '#f0d860', chm: '#706020', chb: '#584810',
        dbg1: '#000848', dbg2: '#101070',
        db1: '#e8e8f0', db2: '#8888c0', db3: '#484888',
        dt: '#ffffff', ds: '#000030',
        hbg: '#000840', hb: '#b0b0d0', hg: '#e8c020', hgr: '#40d840', hr: '#e84040', hbl: '#50a0f0',
        ng: '#f0d850',
        cbg: '#101060', cbo: '#c0c0e0', cc: '#e8e8f0',
        sh: 'rgba(0,0,0,0.3)',
        lp: '#f0d040', lpg: '#fff8d0', lpo: '#e8a020', lpw: '#ffe8a0',
        mk: '#cc3030', mkd: '#a82020', mkc: '#e8e0c0',
        bn: '#886038', bns: '#704828',
        wl: '#788090',
        sa1: '#e0c070', sa2: '#d0b060', sa3: '#c8a050', sa4: '#e8d088', sap: '#907050',
        sa5: '#b8a058', sa6: '#f0e0a0',
        fp1: '#606878', fp2: '#505860', fp3: '#404850', fph: '#d04010', fpf: '#f08030', fpb: '#f0c040',
        fp4: '#707888', fp5: '#e85020',
        moss: '#2a6830',
        mtl1: '#c0c8d0', mtl2: '#909aa8', mtl3: '#606878', mtlh: '#e8f0f8', mtl4: '#485060',
        wdm1: '#7a5030', wdm2: '#946840', wdm3: '#5e4020',
        bkm1: '#707888', bkm2: '#808898', bkm3: '#606070',
        rfm1: '#c04030', rfm2: '#b03828', rfm3: '#d85040',
        stm1: '#6a7880', stm2: '#7a8890', stm3: '#5a6870',
        gsh1: '#0a3010', gsh2: '#0e3818', gsh3: '#124020',
        tkh: '#886040', tkg: '#604020',
        trc: '#0c4810', trd: '#165818',
        pe2: '#7a6040', pe3: '#9a8050',
        wdp: '#081838',
        rk1: '#8b7355', rk2: '#a08868', rk3: '#6b5540', rk4: '#c0a880', rk5: '#504030',
        rk6: '#d8c8a8', rkh: '#e0d0b0', rkd: '#3a2c20', rkm: '#7a6548',
        mv1: '#2a6028', mv2: '#387838', mv3: '#1e4820', mv4: '#4a9048',
        wml: '#f8e8c0', wmd: '#d0b880',
        wms: '#b8d8f8', wmm: '#d0e8ff',
        dsh1: '#1a1420', dsh2: '#281e30',
        hl1: '#fff8e0', hl2: '#f0e0b0',
        g11: '#6adc78', g12: '#92eea0', g13: '#1c6e24', g14: '#3aa842',
        rk7: '#b8a070', rk8: '#907050', rk9: '#c8b890',
        w10: '#6898d0', w11: '#88b8e0', w12: '#a0d0f0',
        bk9: '#b0b8c8', bk10: '#c0c8d0',
        rf7: '#e87060', rf8: '#f09888',
        tk5: '#7a5028', tk6: '#a87840', tk7: '#c89860',
        mv5: '#5aac58', mv6: '#78c870',
        fl1: '#c8b898', fl2: '#d8c8a8', fl3: '#b0a080', fl4: '#a09070'
    };
    function hexToHSL(hex) {
        let r = parseInt(hex.slice(1,3),16)/255, g = parseInt(hex.slice(3,5),16)/255, b = parseInt(hex.slice(5,7),16)/255;
        let mx = Math.max(r,g,b), mn = Math.min(r,g,b), h = 0, s = 0, l = (mx+mn)/2;
        if (mx !== mn) {
            let d = mx - mn;
            s = l > 0.5 ? d / (2-mx-mn) : d / (mx+mn);
            switch(mx) { case r: h=((g-b)/d+(g<b?6:0))*60; break; case g: h=((b-r)/d+2)*60; break; case b: h=((r-g)/d+4)*60; break; }
        }
        return { h: Math.round(h), s: Math.round(s*100), l: Math.round(l*100) };
    }

    function hslHex(h, s, l) {
        s/=100; l/=100;
        const k=n=>(n+h/30)%12, a=s*Math.min(l,1-l), f=n=>l-a*Math.max(-1,Math.min(k(n)-3,9-k(n),1));
        const th=n=>Math.round(n*255).toString(16).padStart(2,'0');
        return '#'+th(f(0))+th(f(8))+th(f(4));
    }

    function shade(c, pct) {
        const n = parseInt(c.replace('#',''),16), a = Math.round(2.55*pct);
        const R=Math.max(0,Math.min(255,(n>>16)+a)), G=Math.max(0,Math.min(255,((n>>8)&0xFF)+a)), B=Math.max(0,Math.min(255,(n&0xFF)+a));
        return '#'+(0x1000000+R*0x10000+G*0x100+B).toString(16).slice(1);
    }

    return { C, hexToHSL, hslHex, shade };
})();
