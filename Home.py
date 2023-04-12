#Importando as bibliotecas

import streamlit as st                         # Biblioteca responsável pela criação da interface gráfica

import numpy as np                             # Biblioteca responsável pela geração de números

import matplotlib.pyplot as plt                # Biblioteca responsável pela geração de gráficos

import psapy.FluidProps as FluidProps          # Biblioteca responsável pela geração das propriedades dos fluidos

import psapy.BeggsandBrill as BB               # Biblioteca responsável pelo cálculo do gradiente de pressão

import psapy.Vogel as IPR                      # Biblioteca responsável pelo cálculo da curva IPR

from scipy.interpolate import interp1d         # Biblioteca responsável pelo processo de interpolação

from scipy.optimize import least_squares       # Biblioteca responsável pela determinação do ponto de operação

from streamlit_option_menu import option_menu  # Biblioteca responsável pela criação das abas

from PIL import Image                          # Biblioteca responsável pela upload de imagens

# CSS Customization

page_bg_img = """

<style>
[data-testid="stAppViewContainer"] {

background-image: linear-gradient(#000000, #000000, #000000);
background-size: cover;

#background-color: #000000;

opacity: 0.8;
    
}

[data-testid="stSidebar"] {
    
background-color: ;

background-size: cover;

opacity: 0.8;
    
}

[data-testid="stHeader"] {
    
background-color: #2D070E;
    
</style>

"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# Criação e Personalização das abas
 
selected = option_menu(
        
    menu_title = 'PetroConsulting V.1',
        
    options = ['Home', 'Curva IPR','Curva VLP', 'Análise Nodal', 'Contactos'],
    
    icons = ['house', 'graph-down', 'graph-up', 'shuffle', 'telephone'],
    
    menu_icon = 'cast',
    
    default_index = 0,

    orientation = 'horizontal',
    
    styles={
        "container": {"padding": "5!important", "background-color": "#2D070E"},
        "icon": {"color": "white", "font-size": "12px"}, 
        "nav-link": {"font-size": "13px", "text-align": "center", "padding":"5px", "margin":"5px", "--hover-color": "#051518"},
        "nav-link-selected": {"background-color": "black"},
    }
)    


# Parámetros de reservatório

PR = st.number_input('Pressão do reservatório** (Psia)', value = 5000)     

TR = st.number_input('Temperatura do reservatório** (ºF)', value = 120)    

st.sidebar.markdown('**:red[PROPRIEDADES DO ÓLEO]**')


#Propriedades do óleo

Oil_API  = st.sidebar.number_input('**Densidade do óleo** (API)**', min_value = 1, max_value = 70, value = 30)

def oil_gravity(Oil_API):
        
    oil_gravity = 141.5/(Oil_API+131.5)
        
    return oil_gravity

GOR = st.sidebar.number_input('Razão gás óleo** (scf/STB)', min_value = 0.0, max_value = 50000.0, value = 600.0)


#Propriedades do gás

st.sidebar.markdown('**:red[PROPRIEDADES DO GÁS]**')

Gas_density = st.sidebar.number_input('Densidade relactiva do gás**', min_value = 0.54, max_value = 1.0, value = 0.6)


#Propriedades da água

st.sidebar.markdown('**:red[PROPRIEDADES DA ÁGUA]**')

water_salinity  = st.sidebar.number_input('Salinidade da água (ppm)', min_value = 0, max_value = 1000000, value = 0)

def water_density(water_salinity):
        
    water_density = ((water_salinity/25000) + 62.428)/62.428
        
    return water_density


# Inputs para o cálculo da curva IPR

st.sidebar.markdown('**:red[MODELO DE DARCY PARA IPR]**')

S = st.sidebar.number_input('Skin factor', min_value = 0.0, max_value = 50.0, value = 0.0)

k = st.sidebar.number_input('Permeabilidade da formação** (mD)', min_value = 1, max_value = 5000, value = 250)

h = st.sidebar.number_input('Espessura da formação** (ft)', min_value = 1, max_value = 5000, value = 30)

u = st.sidebar.number_input('Viscosidade do fluido** (cP)', min_value = 0.1, max_value = 1000.0, value = 0.65)

BO = st.sidebar.number_input('Factor - volume formação do óleo** (bbl/STB)', min_value = 1.0, max_value = 2.0, value = 1.34)

re = st.sidebar.number_input('Raio de drenagem do poço** (ft)', min_value = 1, max_value = 5000, value = 1500)

rw = st.sidebar.number_input('Raio do poço** (ft)', min_value = 0.1, max_value = 3.0, value = 0.328, format = '%.3f')


# Página Home

if selected == 'Home':
       
    image=Image.open('logoblack.jpeg')
    
    st.image(image)
    

# Página 'Curva IPR'

if selected == 'Curva IPR':
    
    st.subheader('**:blue[INFLOW PERFORMANCE RELATIONSHIP - IPR]**')

    PB = FluidProps.Pbub(TR, 75, 100, Gas_density, Oil_API, GOR)
    
    step_size = 100
    
    # Cálculo da vazão de óleo e água

    def oil_rate(QL, WC):
        
        oil_rate = QL*(1-0.01*WC)
        
        return oil_rate


    def water_rate(QL, WC):
        
        water_rate = (WC*QL)/100
        
        return water_rate


    # Modelo de IPR combinado

    IPR_comb = IPR.Vogel_DarcyIPR(PR, k, h , u, re, rw, S, BO, TR, PB, step_size)

    def Qmax():
        
        Qmax= max(list(IPR_comb[0]))
        
        return Qmax

    
    Curva_IPR = st.button('Plotar a curva IPR')

    # Gerando o gráfico
    
    if Curva_IPR:

        plt.style.use('classic')
        
        plt.figure(figsize = (4,2))
            
        fig, ax = plt.subplots()
        
        plt.title('Curva IPR')
        
        ax.set_xlabel ('Vazão de produção (STB/d)', fontsize = 12)
        
        ax.set_ylabel('Pressão (Psia)', fontsize = 12)

        ax.plot(IPR_comb[0], IPR_comb[1])
        
        plt.grid()

        st.pyplot(fig)


# Página 'Curva VLP'

if selected == 'Curva VLP':
       
    st.markdown('**:red[DADOS DE PRODUÇÃO]**')

    TWH = st.number_input('Temperatura na cabeça do poço** (ºF)', min_value = 0.0, max_value = 500.0, value = 90.0)

    PWH = st.number_input('Pressão na cabeça do poço** (Psia)', min_value = 0.0, max_value = 5000.0, value = 1000.0)

    WC = st.number_input('Water cut (%)', min_value = 0, max_value = 100, value = 0)

    QL = st.number_input('Vazão de produção do líquido** (STB/d)', min_value = 0.0, max_value = 50000.0, value = 4000.0)

    st.markdown('**:red[INFORMAÇÕES DO POÇO]**')

    angle = 90 #tubulação vertical

    L = st.number_input('Comprimento da coluna** (ft)', min_value = 500, max_value = 30000, value = 5000)

    D = st.slider('Diâmetro da coluna** (in)', min_value = 2.0, max_value = 20.0, value = 10.0, format = '%.4f')

    st.subheader('**:blue[VERTICAL LIFT PERFORMANCE - VLP]**')
    
    step_size = 100

    # Gradiente de temperatura
    
    def temp_gradient(t0,t1,L):
        
        if L==0:
            
            return 0
        
        else:
            
            return abs(t0-t1)/L
        
    t_grad = temp_gradient(TWH, TR, L)

    Depths = np.linspace(0, L ,step_size)

    temps = TWH + t_grad*Depths

    PB = FluidProps.Pbub(TR, 75, 100, Gas_density, Oil_API, GOR)


    def oil_rate(QL, WC):
        
        oil_rate = QL*(1-0.01*WC)
        
        return oil_rate


    def water_rate(QL, WC):
        
        water_rate = (WC*QL)/100
        
        return water_rate


    # Modelo de IPR combinado

    IPR_comb = IPR.Vogel_DarcyIPR(PR, k, h , u, re, rw, S, BO, TR, PB, step_size)

    def Qmax():
        
        Qmax= max(list(IPR_comb[0]))
        
        return Qmax

    # Cálculo do gradiente de pressão 

    def pressure_transverse(QL):
        
        p = []
        
        dpdz = []
        
        for i in range(len(Depths)):
            
            if i==0:
                
                p.append(PWH)
                
            else:
                
                dz =(Depths[i]- Depths[i-1])
                        
                Pressure = p[i-1]+dz*dpdz[i-1]
                
                p.append(Pressure)
                
            dpdz_step = BB.Pgrad(p[i], temps[i], oil_rate(QL, WC), water_rate(QL, WC), GOR, Gas_density, Oil_API, water_density(water_salinity), D, angle)
            
            dpdz.append(dpdz_step)
              
        return p, dpdz

    p, dpdz = pressure_transverse(QL)

    # Geração da curva VLP

    def vlp(rates):
        
        bhps =[]
        
        for q in rates:
            
            p, dpdz = pressure_transverse(q)
            
            bhp = p[-1]
            
            bhps.append(bhp)
        
        return bhps

    rates = np.linspace(QL, Qmax(), 50)

    bhps = vlp(rates)


    Curva_VLP = st.button('Plotar a curva VLP')

    # Gerando o gráfico
    
    if Curva_VLP:

        plt.style.use('classic')
        
        plt.figure(figsize = (4,2))
            
        fig, ax = plt.subplots()
        
        plt.title('Curva IPR')
        
        ax.set_xlabel ('Vazão de produção (STB/d)', fontsize = 12)
        
        ax.set_ylabel('Pressão (Psia)', fontsize = 12)

        ax.plot(rates, bhps)
        
        plt.grid()

        st.pyplot(fig)
    


# Página 'Análise nodal'

if selected == 'Análise Nodal':
    
    st.markdown('**:red[DADOS DE PRODUÇÃO]**')

    TWH = st.number_input('Temperatura na cabeça do poço** (ºF)', min_value = 0.0, max_value = 500.0, value = 90.0)

    PWH = st.number_input('Pressão na cabeça do poço** (Psia)', min_value = 0.0, max_value = 5000.0, value = 1000.0)

    WC = st.number_input('Water cut (%)', min_value = 0, max_value = 100, value = 0)

    QL = st.number_input('Vazão de produção do líquido** (STB/d)', min_value = 0.0, max_value = 50000.0, value = 4000.0)

    st.markdown('**:red[INFORMAÇÕES DO POÇO]**')

    angle = 90 #tubulação vertical

    L = st.number_input('Comprimento da coluna** (ft)', min_value = 500, max_value = 30000, value = 5000)

    D = st.slider('Diâmetro da coluna** (in)', min_value = 2.0, max_value = 20.0, value = 10.0, format = '%.4f')

    st.subheader('**:blue[ANÁLISE NODAL]**')
    
    step_size = 100

    # Gradiente de temperatura
    
    def temp_gradient(t0,t1,L):
        
        if L==0:
            
            return 0
        
        else:
            
            return abs(t0-t1)/L
        
    t_grad = temp_gradient(TWH, TR, L)

    Depths = np.linspace(0, L ,step_size)

    temps = TWH + t_grad*Depths

    PB = FluidProps.Pbub(TR, 75, 100, Gas_density, Oil_API, GOR)


    def oil_rate(QL, WC):
        
        oil_rate = QL*(1-0.01*WC)
        
        return oil_rate


    def water_rate(QL, WC):
        
        water_rate = (WC*QL)/100
        
        return water_rate


    # Modelo de IPR combinado

    IPR_comb = IPR.Vogel_DarcyIPR(PR, k, h , u, re, rw, S, BO, TR, PB, step_size)

    def Qmax():
        
        Qmax= max(list(IPR_comb[0]))
        
        return Qmax

    # Cálculo do gradiente de pressão 

    def pressure_transverse(QL):
        
        p = []
        
        dpdz = []
        
        for i in range(len(Depths)):
            
            if i==0:
                
                p.append(PWH)
                
            else:
                
                dz =(Depths[i]- Depths[i-1])
                        
                Pressure = p[i-1]+dz*dpdz[i-1]
                
                p.append(Pressure)
                
            dpdz_step = BB.Pgrad(p[i], temps[i], oil_rate(QL, WC), water_rate(QL, WC), GOR, Gas_density, Oil_API, water_density(water_salinity), D, angle)
            
            dpdz.append(dpdz_step)
              
        return p, dpdz

    p, dpdz = pressure_transverse(QL)

    # Geração da curva VLP

    def vlp(rates):
        
        bhps =[]
        
        for q in rates:
            
            p, dpdz = pressure_transverse(q)
            
            bhp = p[-1]
            
            bhps.append(bhp)
        
        return bhps

    rates = np.linspace(QL, Qmax(), 50)

    bhps = vlp(rates)


    Curva_VLP_IPR = st.button('Calcular o ponto de operação do poço')

    if Curva_VLP_IPR:

        plt.style.use('classic')
        
        plt.figure(figsize = (4,2))
            
        fig, ax = plt.subplots()
        
        plt.title('Curva IPR')
        
        ax.set_xlabel ('Vazão de produção (STB/d)', fontsize = 12)
        
        ax.set_ylabel('Pressão (Psia)', fontsize = 12)

        ax.plot(IPR_comb[0], IPR_comb[1], rates, bhps, '-')
        
        plt.grid()

        st.pyplot(fig)
    
    
if selected =='Contactos':
    
    image=Image.open('logoblack.jpeg')
    
    st.image(image)

