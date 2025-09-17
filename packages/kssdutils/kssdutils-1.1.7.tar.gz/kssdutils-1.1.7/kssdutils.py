import os
import random
import string
import time
import operator
import kssdtool
# import kssdtree
import platform


def rs():
    letters = string.ascii_lowercase
    numbers = string.digits
    random_letters = ''.join(random.choice(letters) for i in range(6))
    random_numbers = ''.join(random.choice(numbers) for i in range(3))
    return random_letters + random_numbers


def randomcolor():
    colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color


def str_insert(str_origin, pos, str_add):
    str_list = list(str_origin)
    str_list.insert(pos, str_add)
    str_out = ''.join(str_list)
    return str_out


def allowed_file(filename):
    allowed_extensions = ['.fa', '.fa.gz', '.fasta', '.fasta.gz', '.fna', '.fna.gz', '.fastq', '.fastq.gz', '.fq',
                          'fq.gz']
    return any(filename.endswith(ext) for ext in allowed_extensions)


def create_mat(filename):
    qrys = []
    refs = []
    dists = []
    with open('distout/distance.out', 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split()
            if '.fq' in parts[0]:
                if '/' in parts[0]:
                    qry = parts[0].split('/')[-1].split('.fq')[0]
                else:
                    qry = parts[0].split('.fq')[0]
            elif '.fastq' in parts[0]:
                if '/' in parts[0]:
                    qry = parts[0].split('/')[-1].split('.fastq')[0]
                else:
                    qry = parts[0].split('.fastq')[0]
            elif '.fq.gz' in parts[0]:
                if '/' in parts[0]:
                    qry = parts[0].split('/')[-1].split('.fq.gz')[0]
                else:
                    qry = parts[0].split('.fq.gz')[0]
            elif '.fastq.gz' in parts[0]:
                if '/' in parts[0]:
                    qry = parts[0].split('/')[-1].split('.fastq.gz')[0]
                else:
                    qry = parts[0].split('.fastq.gz')[0]
            elif '.fa' in parts[0]:
                if '/' in parts[0]:
                    qry = parts[0].split('/')[-1].split('.fa')[0]
                else:
                    qry = parts[0].split('.fa')[0]
            elif '.fasta' in parts[0]:
                if '/' in parts[0]:
                    qry = parts[0].split('/')[-1].split('.fasta')[0]
                else:
                    qry = parts[0].split('.fasta')[0]
            else:
                qry = parts[0]

            if '.fa' in parts[1]:
                if '/' in parts[1]:
                    ref = parts[1].split('/')[-1].split('.fa')[0]
                else:
                    ref = parts[1].split('.fa')[0]
            elif '.fasta' in parts[1]:
                if '/' in parts[1]:
                    ref = parts[1].split('/')[-1].split('.fasta')[0]
                else:
                    ref = parts[1].split('.fasta')[0]
            else:
                ref = parts[1]
            dist = parts[4]
            qrys.append(qry)
            refs.append(ref)
            dists.append(dist)
    qrys = qrys[1:]
    refs = refs[1:]
    dists = dists[1:]
    qrys_set = list(set(qrys))
    refs_set = list(set(refs))
    distance_matrix = {}
    for q in qrys_set:
        distance_matrix[q] = {}
        for r in refs_set:
            distance_matrix[q][r] = None
    for q, r, d in zip(qrys, refs, dists):
        distance_matrix[q][r] = d
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as output_file:
        output_file.write("\t".join([""] + refs_set) + "\n")
        for q in qrys_set:
            row = [q] + [distance_matrix[q][r] for r in refs_set]
            output_file.write("\t".join(map(str, row)) + "\n")


def sketch(shuf_file=None, genome_files=None, output=None, abundance=None, set_opt=None):
    if shuf_file is not None and genome_files is not None and output is not None:
        if not os.path.exists(genome_files):
            print('No such file or directory: ', genome_files)
            return False
        if set_opt is None:
            set_opt = False
        if abundance is None:
            abundance = False
        if not allowed_file(genome_files):
            for filename in os.listdir(genome_files):
                if not allowed_file(filename):
                    print('Genome format error for file:', filename)
                    return False
        if not os.path.exists(shuf_file):
            print('No such file: ', shuf_file)
            return False
        print('Sketching...')
        start = time.time()
        if abundance:
            a = 'abundance'
        else:
            a = ''

        system = platform.system()

        # if os.path.isdir(genome_files):
        #     genome_files_list = os.listdir(genome_files)
        #     if system == 'Windows' and not genome_files_list[0].endswith('.gz'):
        #         pipecmd = ''
        #     else:
        #         pipecmd = ''
        # else:
        #     if system == 'Windows' and not genome_files.endswith('.gz'):
        #         pipecmd = ''
        #     else:
        #         pipecmd = ''

        if set_opt:
            kssdtool.dist_dispatch(shuf_file, genome_files, output, 1, 0, 0, '', a)
        else:
            kssdtool.dist_dispatch(shuf_file, genome_files, output, 0, 0, 0, '', a)
        end = time.time()
        print('Sketch spend time：%.2fs' % (end - start))
        print('Sketch finished!')
        return True
    else:
        print('Args error!!!')
        return False


def dist(ref_sketch=None, qry_sketch=None, output=None, metric=None, N=None, flag=None):
    if ref_sketch is not None and qry_sketch is not None and output is not None:
        if not os.path.exists(ref_sketch):
            print('No such file or directory: ', ref_sketch)
            return False
        if not os.path.exists(qry_sketch):
            print('No such file or directory: ', qry_sketch)
            return False
        if flag is None:
            flag = 0
        if metric is None:
            metric = 'mash'

        print('Disting...')
        start = time.time()
        if '/' in output:
            output_dir = os.path.dirname(output)
            output_name = output.split('/')[-1]
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print("Created directory:", output_dir)
        else:
            output_name = output
        if output_name.endswith(".phy") or output_name.endswith(".phylip"):
            if metric not in ['mash', 'aaf']:
                print('Metric type error, only supports mash or aaf distance')
                return False
            else:
                if ref_sketch == qry_sketch:
                    if N is not None:
                        print('Error: N is None when ref_sketch and qry_sketch is same.')
                        return False
                    kssdtool.dist_dispatch(ref_sketch, output, qry_sketch, 2, 0, flag, metric, '')
                    end = time.time()
                    print('Dist spend time：%.2fs' % (end - start))
                    print('Dist finished!')
                    return True
                else:
                    print('Error: ref_sketch and qry_sketch must be same in .phylip (.phy) format.')
                    return False
        elif output_name.endswith(".mat"):
            if metric not in ['mash', 'aaf']:
                print('Metric type error, only supports mash or aaf distance')
                return False
            else:
                if N is not None:
                    kssdtool.dist_dispatch(ref_sketch, output, qry_sketch, 2, N, flag, metric, '')
                else:
                    kssdtool.dist_dispatch(ref_sketch, output, qry_sketch, 2, 0, flag, metric, '')
                end = time.time()
                print('Dist spend time：%.2fs' % (end - start))
                print('Dist finished!')
                if ref_sketch != qry_sketch:
                    os.remove(output)
                    # filename = output.split('/')[-1]
                    create_mat(output)
                return True
        else:
            print('Output type error, only supports .mat and .phylip (.phy) format:', output_name)
            return False
    else:
        print('Args error!!!')
        return False

# def combine(genome_sketch1=None, genome_sketch2=None, output=None):
#     if genome_sketch1 is not None and genome_sketch2 is not None and output is not None:
#         if not os.path.exists(genome_sketch1):
#             print('No such file or directory: ', genome_sketch1)
#             return False
#         if not os.path.exists(genome_sketch2):
#             print('No such file or directory: ', genome_sketch2)
#             return False
#         kssdtool.dist_dispatch(output, genome_sketch1, genome_sketch2, 3, 0, 0, '', '')
#         return True
#
#
# def getlist(genome_sketch=None, output=None):
#     if genome_sketch is not None and output is not None:
#         if not os.path.exists(genome_sketch):
#             print('No such file or directory: ', genome_sketch)
#             return False
#         kssdtool.print_gnames(genome_sketch, output)
#         return True
#
#
# def view_tree(newick, taxonomy, mode):
#     from ete3 import PhyloTree, TreeStyle, NodeStyle, faces, AttrFace, CircleFace, TextFace
#     def layout(node):
#         if node.is_leaf():
#             if node.species in species_colors:
#                 C = CircleFace(radius=8, color=species_colors.get(node.species), style="circle")
#                 C.opacity = 1
#                 faces.add_face_to_node(C, node, 0, position="aligned")
#                 N = AttrFace("name", fsize=14, fgcolor="black")
#                 faces.add_face_to_node(N, node, 0)
#                 style1 = NodeStyle()
#                 style1["fgcolor"] = species_colors.get(node.species)
#                 style1["size"] = 2
#                 style1["vt_line_color"] = species_colors.get(node.species)
#                 style1["hz_line_color"] = species_colors.get(node.species)
#                 style1["vt_line_width"] = 1
#                 style1["hz_line_width"] = 1
#                 style1["vt_line_type"] = 0
#                 style1["hz_line_type"] = 0
#                 node.img_style = style1
#             else:
#                 N = AttrFace("name", fsize=20, fgcolor="red")
#                 faces.add_face_to_node(N, node, 0)
#
#     current_directory = os.getcwd()
#     taxonomy_path = os.path.join(current_directory, taxonomy)
#     if not os.path.exists(taxonomy_path):
#         print('"The file taxonomy txt does not exist."')
#         return
#
#     all_accessions = []
#     accession_taxonomy = {}
#     with open(taxonomy_path, 'r') as file:
#         for line in file:
#             columns = line.split()
#             column_1 = columns[0]
#             column_2 = columns[1:]
#             tempfile = ''
#             for x in column_2:
#                 tempfile = tempfile + x + ' '
#             tempfile = tempfile[:-1]
#             all_accessions.append(column_1)
#             accession_taxonomy[column_1] = tempfile
#
#     known_species = []
#     for x in all_accessions:
#         if accession_taxonomy[x] != 'Unknown':
#             known_species.append(accession_taxonomy[x])
#
#     temp_nwk = 'temp_kssdtree.newick'
#
#     with open(newick, 'r') as f:
#         lines = f.readlines()[0]
#         for x in all_accessions:
#             x_len = len(x)
#             x_index = lines.index(x)
#             loc_index = x_index + x_len + 8
#             if x in accession_taxonomy.keys():
#                 lines = str_insert(lines, loc_index, '[&&NHX:species=' + accession_taxonomy.get(x) + ']')
#             else:
#                 lines = str_insert(lines, loc_index, '[&&NHX:species=NewSpecies]')
#     if os.path.exists(temp_nwk):
#         os.remove(temp_nwk)
#     with open(temp_nwk, 'w') as f:
#         f.write(lines)
#     unique_species = list(set(known_species))
#     species_colors = {}
#
#     temp_color1s = ['#9987ce', '#63b2ee']
#     temp_color2s = ['#9987ce', '#63b2ee', '#76da91']
#     for i in range(len(unique_species)):
#         if len(unique_species) == 1:
#             species_colors[unique_species[i]] = '#9987ce'
#         elif len(unique_species) == 2:
#             species_colors[unique_species[i]] = temp_color1s[i]
#         elif len(unique_species) == 3:
#             species_colors[unique_species[i]] = temp_color2s[i]
#         else:
#             species_colors[unique_species[i]] = randomcolor()
#     species_colors = dict(sorted(species_colors.items(), key=operator.itemgetter(0)))
#     t = PhyloTree(temp_nwk, sp_naming_function=None)
#     for n in t.traverse():
#         n.add_features(weight=random.randint(0, 50))
#     ts = TreeStyle()
#     ts.layout_fn = layout
#     ts.mode = mode
#     ts.show_leaf_name = False
#     ts.show_branch_length = True
#     ts.margin_bottom = 6
#     ts.margin_top = 6
#     ts.margin_left = 6
#     ts.margin_right = 6
#     ts.branch_vertical_margin = 10
#     ts.extra_branch_line_type = 0
#     ts.extra_branch_line_color = 'black'
#     for species, color in species_colors.items():
#         ts.legend.add_face(CircleFace(radius=8, color=color, style="circle"), column=0)
#         ts.legend.add_face(TextFace(text=" " + species, fsize=14, fgcolor="black"), column=1)
#     ts.legend_position = 4
#     for node in t.traverse():
#         if node.species == "NewSpecies":
#             nst = NodeStyle()
#             nst["bgcolor"] = "LightGrey"
#             nst["fgcolor"] = "red"
#             nst["shape"] = "circle"
#             nst["vt_line_color"] = "red"
#             nst["hz_line_color"] = "red"
#             nst["vt_line_width"] = 2
#             nst["hz_line_width"] = 2
#             nst["vt_line_type"] = 0
#             nst["hz_line_type"] = 0
#             node.img_style = nst
#             node.set_style(nst)
#     t.show(tree_style=ts)
#
#
# def place1(shuf_file=None, ref_genome_files=None, qry_genome_files=None, output=None):
#     if shuf_file is not None and ref_genome_files is not None and qry_genome_files is not None and output is not None:
#         if not os.path.exists(ref_genome_files):
#             print('No such file or directory: ', ref_genome_files)
#             return False
#         if not os.path.exists(qry_genome_files):
#             print('No such file or directory: ', qry_genome_files)
#             return False
#         if '/' in output:
#             output_dir = os.path.dirname(output)
#             output_name = output.split('/')[-1]
#             if not os.path.exists(output_dir):
#                 os.makedirs(output_dir)
#                 print("Created directory:", output_dir)
#         else:
#             output_name = output
#         if output_name.endswith(".newick"):
#             timeStamp = int(time.mktime(time.localtime(time.time())))
#             temp_ref_sketch = rs() + '_ref_sketch_' + str(timeStamp)
#             temp_qry_sketch = rs() + '_qry_sketch_' + str(timeStamp)
#             temp_combine_sketch = rs() + '_combine_sketch_' + str(timeStamp)
#             temp_phy = rs() + '.phy'
#             s1 = kssdtree.sketch(shuf_file=shuf_file, genome_files=ref_genome_files, output=temp_ref_sketch,
#                                  set_opt=True)
#             s2 = kssdtree.sketch(shuf_file=shuf_file, genome_files=qry_genome_files, output=temp_qry_sketch,
#                                  set_opt=True)
#             s3 = combine(genome_sketch1=temp_ref_sketch, genome_sketch2=temp_qry_sketch, output=temp_combine_sketch)
#             s4 = kssdtree.dist(genome_sketch=temp_combine_sketch, output=temp_phy, flag=0)
#             s5 = kssdtree.build(phylip=temp_phy, output=output, method='nj')
#             s6 = getlist(genome_sketch=temp_ref_sketch, output='ref.txt')
#             s7 = getlist(genome_sketch=temp_qry_sketch, output='qry.txt')
#             with open('ref.txt', 'r') as ref_file:
#                 ref_lines = ref_file.readlines()
#             with open('qry.txt', 'r') as qry_file:
#                 qry_lines = qry_file.readlines()
#
#             with open('ref_qry.txt', 'w') as result_file:
#                 for line in ref_lines:
#                     result_file.write(line.strip().split('/')[-1].split('.fa')[0] + '\tKnown\n')
#                 for line in qry_lines:
#                     result_file.write(line.strip().split('/')[-1].split('.fa')[0] + '\tUnknown\n')
#             view_tree(newick=output, taxonomy='ref_qry.txt', mode='r')
#         else:
#             print('Output type error, only supports .newick format:', output_name)
#             return False
#     else:
#         print('Args error!!!')
#         return False
#
#
# def place2(shuf_file=None, ref_genome_files=None, qry_genome_files=None, output=None):
#     if shuf_file is not None and ref_genome_files is not None and qry_genome_files is not None and output is not None:
#         if not os.path.exists(ref_genome_files):
#             print('No such file or directory: ', ref_genome_files)
#             return False
#         if not os.path.exists(qry_genome_files):
#             print('No such file or directory: ', qry_genome_files)
#             return False
#         if '/' in output:
#             output_dir = os.path.dirname(output)
#             output_name = output.split('/')[-1]
#             if not os.path.exists(output_dir):
#                 os.makedirs(output_dir)
#                 print("Created directory:", output_dir)
#         else:
#             output_name = output
#         if output_name.endswith(".jplace"):
#             timeStamp = int(time.mktime(time.localtime(time.time())))
#             temp_ref_sketch = rs() + '_sketch_' + str(timeStamp)
#             temp_qry_sketch = rs() + '_sketch_' + str(timeStamp)
#             ref_phy = rs() + '_ref.phy'
#             ref_tree = ref_genome_files + '.newick'
#             s1 = kssdtree.sketch(shuf_file=shuf_file, genome_files=ref_genome_files, output=temp_ref_sketch,
#                                  set_opt=True)
#             s2 = kssdtree.dist(genome_sketch=temp_ref_sketch, output=ref_phy, flag=0)
#             s3 = kssdtree.build(phylip=ref_phy, output=ref_tree, method='nj')
#             s4 = kssdtree.sketch(shuf_file=shuf_file, genome_files=qry_genome_files, output=temp_qry_sketch,
#                                  set_opt=True)
#             ref_qry_phy = 'ref_qry.phy'
#             ref_qry_mat = 'ref_qry.mat'
#             s5 = dist(ref_sketch=temp_ref_sketch, qry_sketch=temp_qry_sketch, output=ref_qry_phy, flag=0)
#             cmd = f'run_apples.py -d {ref_qry_mat} -t {ref_tree} -o {output}'
#             os.system(cmd)
#         else:
#             print('Output type error, only supports .jplace format:', output_name)
#             return False
#     else:
#         print('Args error!!!')
#         return False
