window.RPGColors = (function() {
    const C = {
        g1: '#48b048', g2: '#38a038', g3: '#60c860', g4: '#78d878', gd: '#288828', gdd: '#186018',
        g5: '#90e890', g6: '#105010', g7: '#a0f0a0', g8: '#308830', g9: '#409040', g10: '#208020',
        g11: '#68d068', g12: '#80e080', g13: '#207020', g14: '#50b850',
        gsh1: '#184818', gsh2: '#205020', gsh3: '#286028',

        p1: '#d8c090', p2: '#c8b080', p3: '#b8a070', p4: '#e8d0a0', pe: '#a08850', pm: '#907848',
        p5: '#b09060', p6: '#e0c898', p7: '#c8b888', pe2: '#988060', pe3: '#b09870',

        w1: '#2860c0', w2: '#3070d0', w3: '#1850a8', w4: '#4080e0', wf: '#a0d0ff', ws: '#5890d8',
        wd: '#1040a0', wsp: '#d0e8ff', w5: '#4888e8', w6: '#102858', w7: '#2058b0',
        w8: '#60a0e0', w9: '#284098', w10: '#78b8e8', w11: '#90c8f0', w12: '#a8d8f8',
        wdp: '#0c2048', wms: '#c0d8f8', wmm: '#d8e8ff',

        bk1: '#a0a8c0', bk2: '#8890a8', bk3: '#b0b8d0', bk4: '#c0c8e0', bkl: '#606880', bkd: '#505868',
        bkh: '#d0d8e8', bk5: '#404858', bk6: '#c8d0e0', bk7: '#707888', bk8: '#98a0b8',
        bk9: '#d8e0f0', bk10: '#e0e8f0', bkm1: '#8088a0', bkm2: '#909ab0', bkm3: '#707890',

        rf1: '#e05040', rf2: '#e86050', rf3: '#d04030', rf4: '#f07060', rfl: '#a02818', rfh: '#f89888',
        rfs: '#b82020', rf5: '#c03828', rf6: '#d84838', rf7: '#f08878', rf8: '#f8a098',
        rfm1: '#d04838', rfm2: '#c03828', rfm3: '#e86058',

        dr1: '#906838', dr2: '#a87848', dr3: '#704818', drk: '#f0d050', drf: '#805830', drh: '#b88858',
        dr4: '#b08860', dr5: '#604020',

        wn1: '#60a8e0', wn2: '#80c8f8', wn3: '#4890c8', wnf: '#585868', wns: '#b0e0ff', wnc: '#d06850',
        wn4: '#7098c0', wn5: '#4078b0',

        wd1: '#a07848', wd2: '#b89058', wd3: '#886038', wd4: '#c8a068', wdg: '#685028', wdk: '#604830',
        wd5: '#a88858', wd6: '#907048', wd7: '#d0b078',

        st1: '#8898a0', st2: '#98a8b0', st3: '#687880', st4: '#a8b8c0', stm: '#586068',
        st5: '#8898a8', st6: '#708088', st7: '#b0c0c8', stm1: '#788890', stm2: '#889898', stm3: '#687880',

        tr1: '#208830', tr2: '#38a848', tr3: '#107020', tr4: '#48c060', trh: '#60d878', trs: '#085818',
        tr5: '#288028', tr6: '#40a850', trc: '#107818', trd: '#206828',
        tk1: '#705028', tk2: '#886038', tk3: '#583818', tk4: '#785830', tk5: '#906840', tk6: '#a88050', tk7: '#c0a068',
        tkh: '#a07848', tkg: '#785830',

        fr: '#f04858', fy: '#f8e030', fp: '#d050f0', fw: '#f8f0f8', fo: '#f8a040', fb: '#5090f8',

        sg1: '#c89048', sg2: '#d8a858', sg3: '#e8c068', sgp: '#785028', sgd: '#604018',

        pt1: '#5830b0', pt2: '#7840e0', pt3: '#a060f8', pt4: '#c088ff', ptg: '#d8b0ff',

        hg1: '#208030', hg2: '#28a040', hg3: '#38b050', hg4: '#186020', hgs: '#105018',

        ch1: '#e0a838', ch2: '#c08828', ch3: '#a06820', chl: '#f8e068', chm: '#887028', chb: '#685818',

        dbg1: '#081050', dbg2: '#181878',
        db1: '#f0f0f8', db2: '#9898c8', db3: '#585898',
        dt: '#ffffff', ds: '#000838',

        hbg: '#081048', hb: '#b8b8d8', hg: '#f0d028', hgr: '#48e048', hr: '#f04848', hbl: '#60b0f8',
        ng: '#f8e058',
        cbg: '#181868', cbo: '#c8c8e8', cc: '#f0f0f8',
        sh: 'rgba(0,0,0,0.25)',

        lp: '#f8d848', lpg: '#fff8d8', lpo: '#f0b028', lpw: '#ffe8b0',

        mk: '#e03838', mkd: '#b82828', mkc: '#f0e0c8',
        bn: '#a07040', bns: '#886030',
        wl: '#8890a0',

        sa1: '#e8d080', sa2: '#d8c070', sa3: '#d0b060', sa4: '#f0e098', sap: '#a08058',
        sa5: '#c8b068', sa6: '#f8e8b0',

        fp1: '#707888', fp2: '#606870', fp3: '#505860', fph: '#e04818', fpf: '#f89038', fpb: '#f8c848',
        fp4: '#808898', fp5: '#f06028',

        moss: '#389038',
        mtl1: '#c8d0d8', mtl2: '#a0a8b8', mtl3: '#707888', mtlh: '#e8f0f8', mtl4: '#586070',
        wdm1: '#906038', wdm2: '#a87848', wdm3: '#705028',

        fl1: '#d0c0a0', fl2: '#e0d0b0', fl3: '#c0b090', fl4: '#b0a080',

        rk1: '#a08868', rk2: '#b8a078', rk3: '#887048', rk4: '#d0b890', rk5: '#685840',
        rk6: '#e0d0b0', rkh: '#e8d8c0', rkd: '#504030', rkm: '#907858',
        rk7: '#c0a878', rk8: '#a08060', rk9: '#d0c0a0',

        mv1: '#389038', mv2: '#48a048', mv3: '#286828', mv4: '#58b058', mv5: '#68c868', mv6: '#80d880',
        wml: '#f8e8c8', wmd: '#d8c088',
        dsh1: '#201828', dsh2: '#302838',
        hl1: '#fff8e0', hl2: '#f0e0b8'
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
