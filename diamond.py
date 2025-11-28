#!/usr/bin/env python3
"""
Diamond - Empacotador e Compressor de Arquivos
Uso:
    Empacotar e comprimir: diamond --ec "arquivo1" and "arquivo2" and "arquivo3" --output "saida"
    Descomprimir e desempacotar: diamond --un --ec "arquivo.dmd"
"""

import sys
import os
import struct
import zlib
import argparse

class Diamond:
    MAGIC_NUMBER = b'DMD\x01'  # Identificador do formato
    
    @staticmethod
    def empacotar_comprimir(arquivos, output):
        """Empacota múltiplos arquivos e comprime em formato .dmd"""
        if not output.endswith('.dmd'):
            output += '.dmd'
        
        try:
            # Dados empacotados
            dados_empacotados = bytearray()
            
            # Cabeçalho: número de arquivos
            dados_empacotados.extend(struct.pack('I', len(arquivos)))
            
            print(f"📦 Empacotando {len(arquivos)} arquivo(s)...")
            
            for arquivo in arquivos:
                if not os.path.exists(arquivo):
                    print(f"⚠️  Arquivo não encontrado: {arquivo}")
                    continue
                
                # Lê o arquivo
                with open(arquivo, 'rb') as f:
                    conteudo = f.read()
                
                # Nome do arquivo (limitado a 255 caracteres)
                nome = os.path.basename(arquivo)
                nome_bytes = nome.encode('utf-8')
                if len(nome_bytes) > 255:
                    nome_bytes = nome_bytes[:255]
                
                # Adiciona ao pacote:
                # - Tamanho do nome (1 byte)
                # - Nome do arquivo
                # - Tamanho do conteúdo (4 bytes)
                # - Conteúdo do arquivo
                dados_empacotados.append(len(nome_bytes))
                dados_empacotados.extend(nome_bytes)
                dados_empacotados.extend(struct.pack('I', len(conteudo)))
                dados_empacotados.extend(conteudo)
                
                print(f"  ✓ {arquivo} ({len(conteudo)} bytes)")
            
            # Comprime tudo
            print("🗜️  Comprimindo...")
            dados_comprimidos = zlib.compress(dados_empacotados, level=9)
            
            # Salva o arquivo .dmd
            with open(output, 'wb') as f:
                f.write(Diamond.MAGIC_NUMBER)
                f.write(dados_comprimidos)
            
            tamanho_original = len(dados_empacotados)
            tamanho_comprimido = len(dados_comprimidos)
            taxa = (1 - tamanho_comprimido/tamanho_original) * 100
            
            print(f"\n✨ Sucesso!")
            print(f"📄 Arquivo criado: {output}")
            print(f"📊 Tamanho original: {tamanho_original:,} bytes")
            print(f"📊 Tamanho comprimido: {tamanho_comprimido:,} bytes")
            print(f"📊 Taxa de compressão: {taxa:.1f}%")
            
        except Exception as e:
            print(f"❌ Erro ao empacotar: {e}")
            sys.exit(1)
    
    @staticmethod
    def descomprimir_desempacotar(arquivo_dmd, pasta_destino=None):
        """Descomprime e desempacota arquivo .dmd"""
        if not os.path.exists(arquivo_dmd):
            print(f"❌ Arquivo não encontrado: {arquivo_dmd}")
            sys.exit(1)
        
        try:
            # Lê o arquivo .dmd
            with open(arquivo_dmd, 'rb') as f:
                magic = f.read(4)
                
                if magic != Diamond.MAGIC_NUMBER:
                    print("❌ Arquivo não é um formato .dmd válido!")
                    sys.exit(1)
                
                dados_comprimidos = f.read()
            
            print("🗜️  Descomprimindo...")
            dados_descomprimidos = zlib.decompress(dados_comprimidos)
            
            # Define pasta de destino
            if pasta_destino is None:
                pasta_destino = os.path.splitext(arquivo_dmd)[0] + "_extraido"
            
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)
            
            # Desempacota arquivos
            pos = 0
            num_arquivos = struct.unpack('I', dados_descomprimidos[pos:pos+4])[0]
            pos += 4
            
            print(f"📦 Desempacotando {num_arquivos} arquivo(s)...")
            
            for i in range(num_arquivos):
                # Lê tamanho do nome
                tamanho_nome = dados_descomprimidos[pos]
                pos += 1
                
                # Lê nome do arquivo
                nome = dados_descomprimidos[pos:pos+tamanho_nome].decode('utf-8')
                pos += tamanho_nome
                
                # Lê tamanho do conteúdo
                tamanho_conteudo = struct.unpack('I', dados_descomprimidos[pos:pos+4])[0]
                pos += 4
                
                # Lê conteúdo
                conteudo = dados_descomprimidos[pos:pos+tamanho_conteudo]
                pos += tamanho_conteudo
                
                # Salva o arquivo
                caminho_arquivo = os.path.join(pasta_destino, nome)
                with open(caminho_arquivo, 'wb') as f:
                    f.write(conteudo)
                
                print(f"  ✓ {nome} ({tamanho_conteudo} bytes)")
            
            print(f"\n✨ Sucesso!")
            print(f"📁 Arquivos extraídos em: {pasta_destino}")
            
        except Exception as e:
            print(f"❌ Erro ao desempacotar: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Diamond - Empacotador e Compressor de Arquivos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Empacotar e comprimir:
  diamond --ec "arquivo1.txt" and "arquivo2.jpg" and "arquivo3.pdf" --output "meu_pacote"
  
  # Descomprimir e desempacotar:
  diamond --un --ec "meu_pacote.dmd"
        """
    )
    
    parser.add_argument('--ec', nargs='+', help='Arquivos para empacotar e comprimir')
    parser.add_argument('--un', action='store_true', help='Descomprimir e desempacotar')
    parser.add_argument('--output', help='Nome do arquivo de saída (sem extensão)')
    
    args = parser.parse_args()
    
    # Se não houver argumentos, mostra ajuda
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Modo descomprimir
    if args.un:
        if not args.ec or len(args.ec) != 1:
            print("❌ Para descomprimir, use: diamond --un --ec \"arquivo.dmd\"")
            sys.exit(1)
        
        Diamond.descomprimir_desempacotar(args.ec[0])
    
    # Modo comprimir
    elif args.ec:
        # Remove palavras "and" da lista
        arquivos = [f for f in args.ec if f.lower() != 'and']
        
        if not arquivos:
            print("❌ Nenhum arquivo especificado!")
            sys.exit(1)
        
        output = args.output if args.output else "pacote"
        Diamond.empacotar_comprimir(arquivos, output)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()