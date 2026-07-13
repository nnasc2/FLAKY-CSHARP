import xml.etree.ElementTree as ET
import glob
import csv
import sys
from collections import defaultdict

def parse_trx(filepath):
    """Retorna dict {nome_do_teste: outcome} para um arquivo .trx"""
    ns = {'ns': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
    tree = ET.parse(filepath)
    root = tree.getroot()
    results = {}
    for result in root.findall('.//ns:UnitTestResult', ns):
        test_name = result.get('testName')
        outcome = result.get('outcome')
        results[test_name] = outcome
    return results

def main(trx_folder, output_csv):
    all_files = sorted(glob.glob(f"{trx_folder}/*.trx"))
    print(f"Encontrados {len(all_files)} arquivos .trx")

    outcomes = defaultdict(list)

    for f in all_files:
        try:
            results = parse_trx(f)
            for test_name, outcome in results.items():
                outcomes[test_name].append(outcome)
        except Exception as e:
            print(f"Erro ao parsear {f}: {e}")

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['test_name', 'total_runs', 'passed', 'failed', 'label'])
        for test_name, results_list in outcomes.items():
            passed = results_list.count('Passed')
            failed = results_list.count('Failed')
            total = len(results_list)
            if passed > 0 and failed > 0:
                label = 'flaky'
            elif failed == total:
                label = 'broken'
            else:
                label = 'stable'
            writer.writerow([test_name, total, passed, failed, label])

    print(f"Resultado salvo em {output_csv}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])